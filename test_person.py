# project: BMI2002_FA_17 HW_7 (Biomedical Software Engineering I)
# filename: test_person.py
# time: 201712
# modifier: HsiuPing Lin

""" Test Person

:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2017-12-09
:Copyright: 2017, Arthur Goldberg
:License: MIT
"""
import unittest

from person import Person, Gender, PersonError


class TestGender(unittest.TestCase):

    def test_gender(self):
        self.assertEqual(Gender().get_gender('Male'), Gender.MALE)
        self.assertEqual(Gender().get_gender('female'), Gender.FEMALE)
        self.assertEqual(Gender().get_gender('FEMALE'), Gender.FEMALE)
        self.assertEqual(Gender().get_gender('NA'), Gender.UNKNOWN)

        with self.assertRaises(PersonError) as context:
            Gender().get_gender('---')
        self.assertIn('Illegal gender', str(context.exception))


class TestPerson(unittest.TestCase):

    def setUp(self):
        # create a few Persons
        self.child = Person('kid', 'f')
        self.mom = Person('mom', 'f')
        self.dad = Person('dad', 'm')

        # make a deep family history
        # use dict to store people for different generations

        self.generations = 4
        self.people = people = {}
        self.root_child = Person('root_child', Gender.UNKNOWN)
        people[0] = {self.root_child}

        for i in range(1, self.generations):
            people[i] = set()

        def add_parents(child, depth, max_depth):

            if depth+1 < max_depth:
                dad = Person(child.name + '_dad', Gender.MALE)
                mom = Person(child.name + '_mom', Gender.FEMALE)
                people[depth+1].add(dad)
                people[depth+1].add(mom)
                child.set_father(dad)
                child.set_mother(mom)
                add_parents(dad, depth+1, max_depth)
                add_parents(mom, depth+1, max_depth)
        add_parents(self.root_child, 0, self.generations)

    def test_set_mother(self):
        self.child.set_mother(self.mom)
        self.assertEqual(self.child.mother, self.mom)
        self.assertIn(self.child, self.mom.children)

        self.mom.gender = Gender.MALE
        with self.assertRaises(PersonError) as context:
            self.child.set_mother(self.mom)
        self.assertIn('is not female', str(context.exception))

    def test_set_father(self):
        self.child.set_father(self.dad)
        self.assertEqual(self.child.father, self.dad)
        self.assertIn(self.child, self.dad.children)

        self.dad.gender = Gender.FEMALE
        with self.assertRaises(PersonError) as context:
            self.child.set_father(self.dad)
        self.assertIn('is not male', str(context.exception))

    def test_add_child(self):
        self.assertNotIn(self.child, self.mom.children)
        self.mom.add_child(self.child)
        self.assertEqual(self.child.mother, self.mom)
        self.assertIn(self.child, self.mom.children)

        self.assertNotIn(self.child, self.dad.children)
        self.dad.add_child(self.child)
        self.assertEqual(self.child.father, self.dad)
        self.assertIn(self.child, self.dad.children)

    def test_add_child_error(self):
        self.dad.gender = Gender.UNKNOWN
        with self.assertRaises(PersonError) as context:
            self.dad.add_child(self.child)
        self.assertIn('cannot add child', str(context.exception))
        self.assertIn('with unknown gender', str(context.exception))

    def test_remove_father(self):
        self.child.set_father(self.dad)
        self.child.remove_father()
        self.assertNotIn(self.child, self.dad.children)
        self.assertEqual(self.child.father, None)

    def test_remove_father_error(self):
        self.child.father = None
        with self.assertRaises(PersonError) as context:
            self.child.remove_father()
        self.assertIn('father is unknown', str(context.exception))

    def test_remove_mother(self):
        self.child.set_mother(self.mom)
        self.child.remove_mother()
        self.assertNotIn(self.child, self.mom.children)
        self.assertEqual(self.child.mother, None)

    def test_remove_mother_error(self):
        self.child.mother = None
        with self.assertRaises(PersonError) as context:
            self.child.remove_mother()
        self.assertIn('mother is unknown', str(context.exception))

    def test_get_persons_name(self):
        self.assertEqual(self.child.name, Person.get_persons_name(self.child))
        self.child = None
        self.assertEqual(Person.get_persons_name(self.child), 'NA')

    def test_ancestor(self):
        check = set()
        mindepth = 1
        maxdepth = 3
        for i in range(mindepth, maxdepth+1):
            check = check.union(self.people[i])
        self.assertCountEqual(self.root_child.ancestors(mindepth, maxdepth), check)

    def test_ancestor_error(self):
        max_depth = 3
        min_depth = 5
        with self.assertRaises(PersonError) as context:
            self.root_child.ancestors(min_depth, max_depth)
        self.assertIn('less than min_depth', str(context.exception))

    def test_grandparents(self):
        check = set()
        for i in range(2, 3):
            check = check.union(self.people[i])
        self.assertCountEqual(self.root_child.grandparents(), check)

    def test_all_grandparents(self):
        check = set()
        for i in range(3, len(self.people)):
            check = check.union(self.people[i])
        # APG: this test doesn't find the bug in all_grandparents() because self.people is a dict that
        # maps from depth to people at that depth, and depth 3 is great-grandparent (see the
        # definition of min_depth in ancestors()), so grandparents are not found
        self.assertCountEqual(self.root_child.all_grandparents(), check)

    def test_all_ancestors(self):
        check = set()
        for i in range(1, len(self.people)):
            print(i, self.people[i])
            check = check.union(self.people[i])
        self.assertCountEqual(self.root_child.all_ancestors(), check)


if __name__ == '__main__':
    unittest.main()