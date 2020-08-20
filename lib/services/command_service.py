from dataclasses import dataclass


@dataclass
class CommandService:
    def handle_command(self, command):
        if not command['arguments']:
            poll_data = self._handle_basic_command(command)

        return poll_data

    @staticmethod
    def _handle_basic_command(command):
        if command['capability'] == 'st.switch':
            val = command['command']
            attr = 'switch'
        elif command['capability'] in ['st.doorControl', 'st.windowShade']:
            val = 'closed' if command['command'] == 'close' \
                else 'open' if command['command'] == 'open' \
                else command['command']
            attr = 'door' if command['capability'] == 'st.doorControl' \
                else 'windowShade'
        return dict(
            component=command['component'],
            capability=command['capability'],
            value=val,
            attribute=attr
        )
