import mido
from mido.ports import multi_receive


def print_ports(inargs=None):
    for typ in (
        ("input", mido.get_input_names()),
        ("output", mido.get_output_names())
    ):
        print("%s:" % typ[0])
        for port in typ[1]:
            print("  %s" % port)


def print_messages(inargs=None):
    ports = [mido.open_input(name) for name in mido.get_input_names()]
    for port in ports:
        print('Using {}'.format(port))
    print('Waiting for messages...')

    try:
        for message in multi_receive(ports):
            print('Received {}'.format(message))
    except KeyboardInterrupt:
        pass
