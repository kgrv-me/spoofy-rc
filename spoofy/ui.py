from .network import Network
from .settings import Settings
from time import sleep

class CLI():
    """
    UI class of CLI type to run program for user interaction.
    """
    #: Hold command for processing
    cmd = ''

    @classmethod
    def input_(cls, msg):
        """
        Return processed user input.
        """
        cmd = input(msg).strip().lower()
        for char in Settings.sanitize:
            cmd = cmd.replace(char, '')

        if (Settings.get['DEBUG']):
            print(f"{'':2}(d) REPR(CMD): {repr(cmd)}")

        return cmd

    @classmethod
    def process_info_menu(cls):
        """
        Display software/system information.
        """
        sm = Settings.info['system']
        arch_info = '' if sm['ARCH'] in sm['PLATFORM'] else f" ({sm['ARCH']})"

        print()
        print(f"{'':2}Refer to embedded 'README.md' for documentation")
        print(f"{'':2}or visit https://github.com/kgrv-me/spoofy/blob/main/README.md")
        print()

        print(f"{'':2}Software")
        print(f"{'':4}Python {sm['PYTHON']}")
        if ('software' in Settings.info):
            sw = Settings.info['software']
            print(f"{'':4}Spoofy-{sw['OS']}-{sw['ARCH']} {sw['VERSION']}")
        print()

        print(f"{'':2}System")
        print(f"{'':4}{sm['PLATFORM']}{arch_info}")
        print()
        cls.cmd = cls.input_("Press 'Enter' to go back... ")

    @classmethod
    def process_license_menu(cls):
        """
        Display information about license.
        """
        print()
        print(f"{'':2}GNU General Public License v3.0")
        print()
        print(f"{'':2}Refer to embedded 'LICENSE' for details")
        print(f"{'':2}or visit https://github.com/kgrv-me/spoofy/blob/main/LICENSE")
        print()
        print(f"{'':2}(Disclaimer) Use this software at your own risk!")
        print()
        cls.cmd = cls.input_("Press 'Enter' to go back... ")

    @classmethod
    def process_main_menu(cls):
        """
        Process user input on main menu.

        List available hosts for selection.
        """
        # Menu
        print()
        for i, ip in enumerate(Network.get['ip_list']):
            h = Network.get['hosts'][str(ip)]
            ip = str(ip).ljust(Network.get['max_ip_length'])
            print(f"{i:>3}) {ip}  |  {h['mac']}  |  {(h['vendor_tagged'])}")
        print()
        print(f"{'i':>3}) Information")
        print(f"{'l':>3}) GNU GPLv3 License")
        print(f"{'s':>3}) Settings Configuration")
        print()

        # Process commands
        auto_msg = ' temporary' if Settings.get['WAIT_DURATION'] != 0 else ''
        safe_mode = ' ~ SAFE_MODE ~' if Settings.get['SAFE_MODE'] else ''
        cls.cmd = cls.input_(f"Select device to{auto_msg} disconnect (q to quit):{safe_mode} ")
        if (cls.cmd in Settings.commands['info']):
            cls.process_info_menu()
        elif (cls.cmd in Settings.commands['license']):
            cls.process_license_menu()
        elif (cls.cmd in Settings.commands['settings']):
            cls.process_settings_menu()
        elif (cls.cmd.isdecimal() and int(cls.cmd) < len(Network.get['hosts'])):
            index = int(cls.cmd)
            host = Network.get['hosts'][str(Network.get['ip_list'][index])]
            while (
                cls.cmd not in Settings.commands['back']
                and cls.cmd not in Settings.commands['quit']
            ):
                if (
                    Settings.get['WAIT_DURATION'] == 0
                    and cls.cmd not in Settings.commands['revive']
                ):
                    Network.kill(host)
                    sleep(Settings.get['DELAY'])
                    print()
                    cls.cmd = cls.input_(f"Press 'Enter' to revive '{host['vendor']}' (b to go back):{safe_mode} ")
                    if (cls.cmd == ''):
                        cls.cmd = 'revive'
                elif (
                    Settings.get['WAIT_DURATION'] == 0
                    and cls.cmd not in Settings.commands['kill']
                ):
                    Network.revive(host)
                    sleep(Settings.get['DELAY'])
                    print()
                    cls.cmd = cls.input_(f"Press 'Enter' to spoofy '{host['vendor']}' (b to go back):{safe_mode} ")
                    if (cls.cmd == ''):
                        cls.cmd = 'kill'
                else:
                    Network.spoof(host)
                    sleep(Settings.get['DELAY'])
                    print()
                    cls.cmd = cls.input_(f"Press 'Enter' to spoof '{host['vendor']}' again (b to go back):{safe_mode} ")
        elif (
            cls.cmd not in Settings.commands['quit']
            and cls.cmd != ''
        ):
            print(f"{'':2}(e22) Invalid selection!")

    @classmethod
    def process_settings_menu(cls):
        """
        Process user input on settings menu.

        List available settings for selection.
        """
        # Menu
        print()
        print(f"{'n':>3}) Network scan for local hosts")
        print(f"{'r':>3}) Reset settings configuration")
        print(f"{'s':>3}) Toggle 'SAFE_MODE' for spoofing (Current: {Settings.get['SAFE_MODE']})")
        print(f"{'w':>3}) Set 'WAIT_DURATION' to enable auto-revive (Current: {Settings.get['WAIT_DURATION']})")
        print()

        # Process commands
        cls.cmd = cls.input_("Select setting to configure (b to go back): ")
        if (cls.cmd == 'n'):
            Network.initialize()
        elif (cls.cmd == 'r'):
            Settings.reset_settings()
        elif (cls.cmd == 's'):
            Settings.toggle_safe_mode()
        elif (cls.cmd == 'w'):
            cls.cmd = cls.input_("Enter duration (in seconds): ")
            if (cls.cmd.replace('.', '').isdecimal()):
                Settings.set_wait_duration(float(cls.cmd))
            else:
                print(f"{'':2}(e22) Invalid duration for 'WAIT_DURATION'!")
        elif (cls.cmd == '!debug'):
            Settings.toggle_debug_mode()
        elif (
            cls.cmd not in Settings.commands['back']
            and cls.cmd not in Settings.commands['quit']
            and cls.cmd != ''
        ):
            print(f"{'':2}(e22) Invalid setting selection!")

    @classmethod
    def run(cls):
        """
        Main method to run this component.
        """
        print()
        print("Welcome to 'Spoofy'!")
        Settings.initialize()
        Network.initialize()

        while (cls.cmd not in Settings.commands['quit']):
            cls.process_main_menu()
        Network.cleanup()
        print()

    @classmethod
    def terminate(cls, space=True):
        """
        Invoke in case of interruption to properly terminate.

        Parameter:
            space -- (bool/True) pad 2 extra newlines before the message
        """
        if (Network.get_killed() > 0):
            if (space):
                print()
                print()
            print("Initiate cleanup process... DO NOT interrupt!")
        Network.cleanup()
        print()