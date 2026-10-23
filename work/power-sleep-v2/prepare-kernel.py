from pathlib import Path
import difflib
root=Path('/Users/admin/ThorDS/build/thorch-work/packages/linux-thorch')
work=Path('/Users/admin/ThorDS/work/power-sleep-v2')
def patch(original, updated, target, name, explanation, folder='patches'):
    (root/folder/name).write_text(explanation+'\n'+''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile='a/'+target,tofile='b/'+target)))
s=(work/'rsinput.before.c').read_text()
t=s.replace('#include <linux/platform_device.h>', '#include <linux/platform_device.h>\n#include <linux/pm.h>')
needle='static const struct of_device_id rsinput_of_match[] = {'
t=t.replace(needle,'''/* Quiesce reports before the parent UART suspends. Resume restores the MCU. */
static int rsinput_suspend(struct device *dev)
{
    struct rsinput_driver *drv = dev_get_drvdata(dev);

    if (drv->enable_gpio)
        gpiod_set_value_cansleep(drv->enable_gpio, 0);
    if (drv->reset_gpio)
        gpiod_set_value_cansleep(drv->reset_gpio, 0);
    return 0;
}

static int rsinput_resume(struct device *dev)
{
    return rsinput_init_commands(dev_get_drvdata(dev));
}

static DEFINE_SIMPLE_DEV_PM_OPS(rsinput_pm_ops, rsinput_suspend, rsinput_resume);

'''+needle)
t=t.replace('.of_match_table = rsinput_of_match,','.of_match_table = rsinput_of_match,\n        .pm = pm_sleep_ptr(&rsinput_pm_ops),')
patch(s,t,'drivers/input/joystick/rsinput.c','0023-input-rsinput-quiesce-and-restore-mcu-on-sleep.patch','Subject: [PATCH] input: rsinput: quiesce and restore Thor MCU across sleep\n\nAdapted for the pinned ROCKNIX driver from Armada 0508 and 1005.\nSource: https://github.com/armada-os/armada/tree/main/packages/kernel/patches\nOriginally-by: Luke Johnson <jaewun@me.com>\nThis driver has no rumble workqueue; preserve its existing input path.')
s=(work/'thor.before.dts').read_text(); t=s.replace('/dts-v1/;', '/dts-v1/;\n\n#include <dt-bindings/input/gpio-keys.h>')
t=t.replace('gpio-keys-lid {\n\t\tcompatible = "gpio-keys";', 'gpio-keys-lid {\n\t\tcompatible = "gpio-keys";\n\t\tpinctrl-0 = <&hall_lid_n>;\n\t\tpinctrl-names = "default";')
t=t.replace('label = "Hall Lid Sensor";', 'label = "Hall Lid Sensor";\n\t\t\tdebounce-interval = <50>;\n\t\t\twakeup-event-action = <EV_ACT_DEASSERTED>;')
t=t.replace('&tlmm {','''&tlmm {
	hall_lid_n: hall-lid-n-state {
		pins = "gpio17";
		function = "gpio";
		bias-pull-up;
		output-disable;
	};
''')
patch(s,t,'arch/arm64/boot/dts/qcom/qcs8550-ayn-thor.dts','0007-arm64-dts-thor-debounce-lid-open-wake.patch','Subject: [PATCH] arm64: dts: Thor: pull up and debounce lid-open wake\n\nAdapted sleep-only changes from Armada qcs8550-ayn-thor.dts.patch.\nUse the deasserted (open) edge; retain ThorDS display and touch settings.', 'dts-patches')
s=(work/'ayn.before.dtsi').read_text(); needle='linux,code = <KEY_VOLUMEUP>;\n\t\t\tlinux,can-disable;\n\t\t\twakeup-source;'; assert needle in s
t=s.replace(needle,'linux,code = <KEY_VOLUMEUP>;\n\t\t\tlinux,can-disable;')
patch(s,t,'arch/arm64/boot/dts/qcom/qcs8550-ayn-common.dtsi','0008-arm64-dts-ayn-disable-volume-up-wake.patch','Subject: [PATCH] arm64: dts: AYN: do not wake on volume up\n\nAdapted from Armada wake-source policy; do not change SD timings.', 'dts-patches')
p=root/'PKGBUILD';p.write_text(p.read_text().replace('pkgrel=16','pkgrel=17'))
