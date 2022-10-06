import random

# Parameters
NUM_TREES = 3  # Should not be larger than 9
NUM_LAYERS = 3  # Increasing this number, increases the size of the trees exponentially.
MIN_CHILD = 1
MAX_CHILD = 2  # Increasing this number, increases the size of the trees exponentially.


def translate_layer(layer, translation):
    """
    Translates each point in a layer with a vector.
    :param layer: The set of points to be translated.
    :param translation: The translation vector.
    :return: A copy of the vector with the translated points.
    """
    return [(x[0] + translation[0], x[1] + translation[1]) for x in layer]


def get_layer(size):
    """
    Returns a square set of points that form a layer. The layer is exactly 1
    {@code size} bigger in all directions than the square that makes up all
    the possible start nodes. This is a 3x3 grid. This means that for
    {@code size == 1} this method will return a layer of 5x5 (around the 3x3 grid).
    The nodes are also translated such that the 3x3 grid is in the middle, where
    the top left point of the 3x3 grid is at (0,0). To clarify, the 5x5 grid will
    have a top left coordinate of (-1, -1). Each integer combination within the
    5x5 grid will be in the layer (i.e. (-1, -1), (2, 2), (3, 1), etc.).

    If {@code size} is even, we also translate the entire layer by (0.5, 0.5) which
    avoids arcs straight down (we now have an offset).

    :param size: The number of units the grid should be bigger than a 3x3 grid.
    :return: A list including all points within the {@code (3+size*2)x(3+size*2)} grid.
    """
    layer = [(k, m) for k in range(size * 2 + 3) for m in range(size * 2 + 3)]
    layer = translate_layer(layer, (-(size + 1), -(size + 1)))
    if size % 2 == 0:
        layer = translate_layer(layer, (0.5, 0.5))
    return layer


def generate_layers():
    """
    Generates all necessary layers for tree generation.
    This uses global constants {@code NUM_TREES, MAX_CHILD} and {@code NUM_LAYERS}
    in order to compute the size of the layers needed, and the number of layers needed.
    This will keep the trees as close together as possible.
    :return: The list of start nodes and a list of lists where each list is a layer.
    """
    start_nodes = [divmod(i, 3) for i in range(0, NUM_TREES)]
    nodes = []

    ct = 1
    i = 1
    while len(nodes) < NUM_LAYERS:
        layer = get_layer(ct)
        while len(layer) < NUM_TREES * MAX_CHILD ** (len(nodes) + 1):
            ct += 1
            layer = get_layer(ct)
        i += 1
        nodes.append(layer)
    return start_nodes, nodes


class Question:
    """
    This class generates all trees and serves as a data class
    that is able to export all trees to a text file.
    """

    def __init__(self, start_nodes, layers):
        """
        The trees are already generated in the init function.
        :param start_nodes: The list of all root nodes of the trees.
        :param layers: The list of lists of all layers which hold possible nodes for tree generation.
        """
        self.trees = []
        for tree in start_nodes:
            tree = Tree(tree, layers)
            self.trees.append(tree)

    def __str__(self):
        ct = 0
        for tree in self.trees:
            tree.translate(ct)
            ct += tree.num_nodes()

        random_leaf = random.choice(self.trees).get_random_leaf()
        s = "{}\n".format(random_leaf[0])
        s += "ID,x,y,z,parent\n"
        for tree in self.trees:
            s += str(tree)

        return s

    def export(self, filename):
        with open(filename, "w") as f:
            f.write(self.__str__())


class Tree:
    """
    The Tree class represents one tree. The tree is stored
    as a list of nodes where each node is of the following format:

    {@code (ID, x, y, z, parent)}

    The variable {@code parent} refers to the {@code ID} variable of a different
    node, indicating that they are connected.
    """

    def __init__(self, start_node, layers):
        """
        Start the tree generation within the init function.
        At the end of the init function, the tree is constructed completely.

        :param start_node: The root node of the tree
        :param layers: All remaining nodes available per layer.
        """
        self.tree = []
        self.ct = 0
        self.num_layers = len(layers)
        self.generate(start_node, layers, 0, 0)

    def generate(self, node, layers, parent, layer):
        """
        The recursive generate function. This method is called
        recursively using a depth-first approach until the desired
        depth is reached.

        During each call, the following steps occur
        1. {@code node} is added to the tree.
        2. A random number is chosen between {@code MIN_CHILD} and {@code MAX_CHILD} which determines
            the number of children the current node has.
        3. For the amount of the random number, a recursive call is made to add a new node to the tree
            one layer deeper.
        This is done till the tree is complete.
        :param node: The current node which will be added to the tree, and possible have children attached to.
        :param layers: The remaining nodes available per layer.
        :param parent: The parent of {@code node}
        :param layer: The current depth.
        """
        parent = self.add_node(node, parent, layer)
        if layer >= self.num_layers:
            return

        rand = random.randint(MIN_CHILD, MAX_CHILD)
        for i in range(rand):
            new_node = random.choice(layers[layer])
            layers[layer].remove(new_node)

            self.generate(new_node, layers, parent, layer + 1)

    def add_node(self, node, parent, layer):
        """
        Adds {@code node} to the tree. It also updates the node
        counter of the Tree to keep track how many nodes are added.
        This is needed in order to let nodes have a unique ID.
        :param node: The node to be added.
        :param parent: The parent of {@code node}
        :param layer: The current depth.
        :modifies self.ct: {@code self.ct} is incremented by one.
        :return: {@code self.ct - 1} after the modification.
                    This is the ID of the recently added {@code node}.
        """
        self.tree.append((self.ct, node[0], -layer, node[1], parent))
        self.ct += 1
        return self.ct - 1

    def __str__(self):
        s = ""
        for row in self.tree:
            s += "{},{},{},{},{}\n".format(row[0], row[1], row[2] - 1, row[3], row[4])
        return s

    def translate(self, num):
        """
        This method translates the ID's of all nodes by a certain value.
        :param num: The value to be translated by.
        :modifies self.tree: All nodes in the tree are modified.
        """
        for r in range(len(self.tree)):
            row = self.tree[r]
            self.tree[r] = (row[0] + num, row[1], row[2], row[3], row[4] + num)

    def num_nodes(self):
        return len(self.tree)

    def get_random_leaf(self):
        """
        Returns a random leaf of the tree.
        :return: The random leaf.
        """
        return random.choice([row for row in self.tree if row[2] == -self.num_layers])


def main():
    s, gen_layers = generate_layers()
    question = Question(s, gen_layers)
    question.export("question1.txt")


if __name__ == "__main__":
    if NUM_TREES <= 9:
        main()
