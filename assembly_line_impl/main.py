from transitions.extensions import GraphMachine


class AssemblyLine:
    states = [
        {'name': 'Initial', 'on_enter': ['print_state']},
        {'name': 'WaitOp', 'on_enter': ['print_state']},
        {'name': 'PickComponent', 'on_enter': ['print_state']},
        {'name': 'InspectComponent', 'on_enter': ['print_state']},
        {'name': 'DiscardComponent', 'on_enter': ['print_state', 'count_discarded_components']},
        {'name': 'PlaceComponent', 'on_enter': ['print_state']},
        {'name': 'AssembleProduct', 'on_enter': ['print_state']},
        {'name': 'VerifyAssembly', 'on_enter': ['print_state']},
        {'name': 'PackageProduct', 'on_enter': ['print_state']},
        {'name': 'PerformCalibration', 'on_enter': ['print_state']},
        {'name': 'ReturnToHome', 'on_enter': ['print_state']},
        {'name': 'Finish', 'on_enter': ['print_state']}
    ]

    transitions = [
        {'trigger': 'initializing', 'source': 'Initial', 'dest': 'WaitOp'},
        {'trigger': 'receive_command', 'source': 'WaitOp', 'dest': 'PickComponent'},
        {'trigger': 'component_picked', 'source': 'PickComponent', 'dest': 'InspectComponent'},

        {'trigger': 'inspected_component', 'source': 'InspectComponent', 'dest': 'PlaceComponent',
         'unless': ['is_bad_component']},
        {'trigger': 'inspected_component', 'source': 'InspectComponent', 'dest': 'DiscardComponent',
         'conditions': ['is_bad_component']},

        {'trigger': 'component_placed', 'source': 'PlaceComponent', 'dest': 'AssembleProduct'},
        {'trigger': 'assembled_product', 'source': 'AssembleProduct', 'dest': 'VerifyAssembly'},
        {'trigger': 'verified_assembly', 'source': 'VerifyAssembly', 'dest': 'PackageProduct'},

        {'trigger': 'discarded_component', 'source': 'DiscardComponent', 'dest': 'ReturnToHome'},

        # TODO: Fazer a lógica de calibração
        {'trigger': 'max_defective_component', 'source': 'ReturnToHome', 'dest': 'PerformCalibration',
         'conditions': ['max_attempts']},
        {'trigger': 'not_max_defective_component', 'source': 'ReturnToHome', 'dest': 'WaitOp',
         'unless': ['max_attempts']},

        {'trigger': 'packaged_product', 'source': 'PackageProduct', 'dest': 'Finish'},
        {'trigger': 'calibration_finish', 'source': 'PerformCalibration', 'dest': 'Finish'}

    ]

    def __init__(self):
        self.inspected_component_flag = False
        self.max_defective_components = 2
        self.defective_components_count = 0
        self.state_execution_sequence = []

        self.machine = GraphMachine(model=self, states=AssemblyLine.states,
                                    transitions=AssemblyLine.transitions, initial='Initial')

    def print_state(self):
        print('Estado atual: ' + self.state + '\n')

    def count_discarded_components(self):
        self.defective_components_count += 1

    def is_bad_component(self):
        return self.inspected_component_flag

    def max_attempts(self):
        return self.defective_components_count == self.max_defective_components

    def run(self):
        available_transitions = self.machine.get_triggers(self.state)
        available_transitions = available_transitions[len(AssemblyLine.states):]

        for current_transition in range(len(available_transitions)):
            method = getattr(self, available_transitions[current_transition])
            may_method = getattr(self, 'may_' + available_transitions[current_transition])
            if may_method():
                print(f"Transição executada: {available_transitions[current_transition]}")
                method()

        self.state_execution_sequence.append(self.state)


if __name__ == '__main__':
    assembly_line = AssemblyLine()
    assembly_line.inspected_component_flag = False

    while assembly_line.state != 'Finish':
        assembly_line.run()

    assembly_line = AssemblyLine()
    assembly_line.inspected_component_flag = True

    while assembly_line.state != 'Finish':
        assembly_line.run()

    # assembly_line.machine.get_graph().draw('assembly_line.png', prog='dot')

process_machine = AssemblyLine()

# TODO: Tenho que colocar um nome para o processo de forma que eu consiga achar ele rápido
#  ProcessMachine pode ser um nome genérico
