# ThorDS ARM sleep/power port proposal

## Recommendation

Port the **policy and validation** from the newer ARM builds, but keep ThorDS's existing kernel stack and dual-screen session model.

The ThorDS kernel already contains the relevant low-level work:

- UFS suspend/relink and hibern8 handling
- Qualcomm IPCC suspend IRQ handling
- PCIe suspend OPP retention for SM8550 s2idle
- RPMh regulator sleep-state support
- Thor touch-panel power retention
- Thor thermal wake-IRQ filtering
- UART/gamepad suspend-resume fixes

Those patches are already present under `build/thorch-work/packages/linux-thorch/patches/` and the Thor DTS patches. Re-importing the same Armada/ROCKNIX patches would risk duplicate or conflicting hunks.

## Proposed patch

### 1. Add an explicit, reversible sleep-mode selector

Add `/usr/bin/thorch-sleep-mode` to `thorch-bsp`. It should:

- report the kernel's available modes from `/sys/power/mem_sleep`
- default to the current safe `s2idle`
- allow `deep` only when the kernel advertises it
- write a drop-in at `/etc/systemd/sleep.conf.d/60-thorch-sleep-mode.conf`
- refuse to switch while a suspend is active
- print the exact mode selected after every change

Suggested interface:

```
thorch-sleep-mode status
thorch-sleep-mode s2idle
thorch-sleep-mode deep
```

The default remains:

```
[Sleep]
SuspendState=mem
MemorySleepMode=s2idle
```

On a Thor kernel that reports `[s2idle] deep`, `thorch-sleep-mode deep` changes only the selector:

```
[Sleep]
MemorySleepMode=deep
```

This gives us a clean A/B test without replacing the image or touching Android storage.

### 2. Preserve state around sleep, borrowing the safe parts of NovaDeck

Extend `thords-sleep-guard` to save and restore only reversible runtime state:

- current CPU governors
- current GPU devfreq governor
- current Wi-Fi/Bluetooth rfkill state
- both backlight `bl_power` values
- current RGB brightness

Before suspend:

1. stop LAVD, as it does today;
2. blank both panels;
3. optionally use powersave governors and soft-block radios;
4. let the kernel enter suspend.

After resume:

1. restore radios, governors, GPU policy and RGB;
2. unblank both panels unconditionally;
3. restart LAVD only if it was running before sleep;
4. record a pre/post power snapshot.

The state files must be written under `/run/thords-sleep/`, and every operation must be best-effort. A missing sysfs node must never abort resume.

### 3. Do not port NovaDeck's fake-suspend engine

NovaDeck's `novadeck-suspend` freezes Steam's gamescope session cgroup and captures the power key with `libinput --grab`. That is appropriate for Steam Game Mode, but ThorDS uses Sway plus Azahar and has two independently driven panels. Porting it wholesale would create a second compositor/session power owner and could reproduce the black-screen and SSH failures we've already seen.

## Test gate

Before making deep sleep the default:

1. Boot with `s2idle`; run 10 lid-close cycles of 90 seconds.
2. Record wake success, panel state, Wi-Fi reconnect, input, and charge-counter delta.
3. Repeat with `deep` selected.
4. Keep deep only if all 10 cycles resume cleanly and average sleep draw improves materially.
5. If any deep cycle fails, revert to `s2idle` and keep the state-restoration patch.

## Expected result

This should improve lid-close battery drain and resume reliability while retaining Azahar, Mako, dual-screen brightness, CTGP networking, and the current low-battery shutdown guard. The change is intentionally staged so a failed deep-sleep experiment is one command away from rollback.

