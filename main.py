from fsm_reader import FSMReader
from ADS import Sdist, ADSBuilder
from visualize import visualize_FSM, visualize_distinguishing_tree, visualize_ads
from W_method import WMethod


def main():

    file_path = "specification.txt"
    specification = FSMReader(file_path).read_fsm()

    visualize_FSM(specification)

    test_suite = WMethod(specification).generate_test_suite()
    with open("tests.txt", "w", encoding="utf-8") as f:
        f.write("W-метод:\n")
        for seq in test_suite:
            f.write(str(seq) + "\n")

        sdist = Sdist(specification)
        state_tree = sdist.build()

        visualize_distinguishing_tree(state_tree, sdist.start_state)

        test_tree_builder = ADSBuilder(sdist, L=2)
        ads_paths = test_tree_builder.build_test_example()

        f.write("\nРазличающий тестовый пример:\n")
        f.write(test_tree_builder.readable_test(ads_paths, show_states=True) + "\n")

        visualize_ads(ads_paths, test_tree_builder)

if __name__ == "__main__":
    main()
