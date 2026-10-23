# Charging investigation — 21 October 2026

User reports plugged in/lid closed overnight without charging again. Current
physical state initially awake but unplugged. User unsure of order of charger
connection versus closing lid. Asked to reconnect same charger with lid open.
Pending async confirmation: plugged awake / plugged shut down / not plugged yet.

Read-only SSH succeeded via work/edge-aa/ssh-connect.py proxy; direct SSH timed
out. Then proxy also timed out after gauge reached 2%. No device settings changed.

Kernel 7.1.2-thorch19, s2idle. Kernel journal has unbroken suspend Oct20 18:14:26
BST -> Oct21 18:35:23 BST (24h20m57s). Its battery snapshots were overwritten by
subsequent suspend Oct21 18:35:52 ->21:21:39. Cannot prove overnight charging from
remaining latest pre/post files. Latest cycle started/ended Discharging:
46%, 2667813uAh ->38%,2233598uAh over 9946.48s. User was unplugged at inspection.

Important fresh wake gauge issue:
21:21:39: 38%,2233598uAh (post snapshot)
21:22:07: 33%,1901484uAh, current -1341097uA, voltage3393374uV
21:23:17: 2%,145694uAh, current -1797407uA, voltage3319803uV
Such a counter/capacity change is incompatible with measured current over that
interval; gauge/firmware/reporting correction is strongly suggested. Do not
interpret it as that much physical energy consumed in one minute. USB online0
and UCSI online0 while user confirmed unplugged, expected and not proof of
failure to detect a charger. No plugged-in readings obtained yet today.

Battery model reported 8110606_QUECTEL_SA885GLIVESTREAMING2025_6000MAH_AVERAGED_
MASTERSLAVE_SEP18TH2025. That string ALSO occurs in the local reference Armada
Thor firmware, so do not infer wrong firmware from the string alone. Thor
reference adsp.mbn SHA256 e771ab967310bc210147d5d0f9e455802c35564584d1ed26e64a2eb4e9c2470c;
Odin2 reference 750d98172d9e780640fd02431dea2cb6827f11e34e8d2e71109be727bfc1d42d.
Live firmware hashes and remoteproc selected paths still need checking.

Upstream leads (not confirmed our cause):
https://github.com/armada-os/armada/issues/89
https://github.com/ROCKNIX/distribution/commit/47e077d0bb
Thor charger-firmware correction in ROCKNIX; live firmware must be verified.
https://github.com/ROCKNIX/distribution/pull/3126
Current description withdraws gauge-based low standby numbers, says charging
works asleep on tested Odin2. Not a Thor-specific guarantee.

observe.py prepared locally but NOT uploaded/run. Ten-minute read-only sampler
of supply properties every2sec and uniquely archived pre/post snapshots. Need
connect, upload, run with nohup, obtain stable plugged-awake actual battery
current/counter increase. Then short closed-lid test, preserve before/after and
USB negotiation state. User asked no long overnight tests in prior conversation.

## Reconnected after actual shutdown
User reports blue indicator became orange and device died about3min later while
finding lead. It is now plugged and awake; new boot confirms. Fresh21:26:35 sample
Charging3%,181257uAh,current+4052224uA. USB-PD9V, USB8610000uV/2815000uA (~24.2W),
USBonline1 and UCSI PD online1. Live ADSP hashes match its Android-derived Thor
firmware and local Armada Thor reference, and remoteproc selects Thor path:
e771ab...adsp.mbn and660fd8...adsp_dtb.mbn. Firmware-mismatch lead not supported.

observe.py uploaded /home/thords/charging-observe-20261021.py and started nohup.
Ten minutes of AWAKE monotonic time; freezes during actual suspend, resumes after.
Data /home/thords/charging-20261021/samples.jsonl and uniquely archived pre/post.
Local open-comparison.txt proves3%201907uAh ->5%305728uAh in58.32s, +103.821mAh.
Charging ~4.1A consistently. Next physical step: close lid while remaining
plugged, confirm closed, time3min, reopen, inspect archived snapshots plus delayed
awake samples to avoid stale-gauge inference. Do not infer reliability overnight
from one successful short cycle; need preserve evidence of intermittent issue.

## Plugged closed-lid cycle result
Actual s2idle21:31:34 ->21:35:00,206.34485s. PreCharging11%,684304uAh;
postCharging19%,1128271uAh (+443967uAh=443.967 reportedmAh). USB online1 afterwake,
PD~8.6V/2.815A. Refreshed sample21:36:14 remainsCharging21%,1231519uAh,
current+4031349uA. Thus this fresh-boot cycle genuinely charges asleep. Does NOT
prove overnight reliability or establish cause of earlier failure. Raw reads
saved closed-result-initial/refreshed.txt, sampler downloaded samples.jsonl.
No persistent device settings changed; diagnostic observer only writes user logs.
Next discriminating short test: attach charger while ALREADY asleep (order user
unsure lastnight), versus this cycle connected first thenclosed. Need new sampler
run if ten-minute awake capture expires. Do not conclude fixed based on one pass.

## Charger attached while already asleep: different outcome
User unplugged lidopen;21:37:20 baselineDischarging22%,1302072uAh,USBonline0.
Logger restartedPID14972. Userclosedlid, waited, attachedchargerwithoutopening.
Actual s2idle21:37:31.287209 ->21:41:32.714799,241.42759s. PreDischarging22%,
1301498uAh; immediatepostCharging22%,1300924uAh (delta-574uAh, essentiallyflat).
At21:41:49 (17.3s awake)23%,1329031uAh,current+4.13A,USBonline1,PD9V.
At21:42:53 (80.5s awake)24%,1423675uAh,current+4.12A. No delayed catchup of the
~4min asleep interval; awake increase consistent with prior open-lid charging.

Strong evidence for an order-dependent failure: connectedwhileawake thenclosed
charged during sleep; chargerconnected AFTER suspending did not measurably add
charge until wake. Still a firmware/gauge-limited inference, not external USB
meter measurement, and does not prove sole cause of overnight failure. No
persistent system changes made. Workaround: wake/open, connectcharger, confirm
charging starts beforeclosing. Do not claim blanket overnight reliability.
