""" Test RelatedPerson

:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2017-12-09
:Copyright: 2017-2018, Arthur Goldberg
:License: MIT
"""
import unittest

from related_person import RelatedPerson, Gender, RelatedPersonError


class TestGender(unittest.TestCase):

    def test_gender(self):
        self.assertEqual(Gender().get_gender('Male'), Gender.MALE)
        self.assertEqual(Gender().get_gender('NA'), Gender.UNKNOWN)

        with self.assertRaises(RelatedPersonError) as context:
            Gender().get_gender('---')
        self.assertRegex(Gender().genders_string_mappings(), "'f'.* -> 'F'")

class TestRelatedPerson(unittest.TestCase):

    def setUp(self):
        # create a few RelatedPersons
        self.child = RelatedPerson('kid', 'NA')
        self.mom = RelatedPerson('mom', 'f')
        self.dad = RelatedPerson('dad', 'm')

        # make a deep family history
        self.generations = 6
        self.people = people = []
        self.root_child = RelatedPerson('root_child', Gender.UNKNOWN)
        people.append(self.root_child)

        def add_parents(child, depth, max_depth):
            if depth+1 < max_depth:
                dad = RelatedPerson(child.name + '_dad', Gender.MALE)
                mom = RelatedPerson(child.name + '_mom', Gender.FEMALE)
                people.append(dad)
                people.append(mom)
                child.set_father(dad)
                child.set_mother(mom)
                add_parents(dad, depth+1, max_depth)
                add_parents(mom, depth+1, max_depth)
        add_parents(self.root_child, 0, self.generations)

    @staticmethod
    def test_get_related_persons_name():
        assert RelatedPerson.get_related_persons_name(RelatedPerson('test', 'NA')) == 'test'
        assert RelatedPerson.get_related_persons_name(None) == 'NA'

    def test_set_father(self):
        self.child.set_father(self.dad)
        self.assertEqual(self.child.father, self.dad)
        self.assertIn(self.child, self.dad.children)

    def test_set_father_error(self):
        self.dad.gender = Gender.FEMALE
        with self.assertRaises(RelatedPersonError) as context:
            self.child.set_father(self.dad)
        self.assertIn('is not male', str(context.exception))

    def test_set_mother(self):
        self.child.set_mother(self.mom)
        self.assertEqual(self.child.mother, self.mom)
        self.assertIn(self.child, self.mom.children)

    def test_set_mother_error(self):
        self.mom.gender = Gender.MALE
        with self.assertRaises(RelatedPersonError) as context:
            self.child.set_mother(self.mom)
        self.assertIn('is not female', str(context.exception))

    def test_remove_father(self):
        self.child.set_father(self.dad)
        self.child.remove_father()
        self.assertNotIn(self.child, self.dad.children)
        self.assertEqual(self.child.father, None)

    def test_remove_father_error(self):
        with self.assertRaises(RelatedPersonError) as context:
            self.child.remove_father()
        self.assertIn('as it is not set', str(context.exception))

        self.child.father = RelatedPerson('test', 'M')
        with self.assertRaises(RelatedPersonError) as context:
            self.child.remove_father()
        self.assertIn('not one of his children', str(context.exception))

    def test_remove_mother(self):
        self.child.set_mother(self.mom)
        self.child.remove_mother()
        self.assertNotIn(self.child, self.mom.children)
        self.assertEqual(self.child.mother, None)

    def test_remove_mother_error(self):
        with self.assertRaises(RelatedPersonError) as context:
            self.child.remove_mother()
        self.assertIn('is not set and cannot be removed', str(context.exception))

        self.child.mother = RelatedPerson('test', 'F')
        with self.assertRaises(RelatedPersonError) as context:
            self.child.remove_mother()
        self.assertIn('not one of her children', str(context.exception))

    def test_add_child(self):
        self.dad.add_child(self.child)
        self.assertIn(self.child, self.dad.children)
        self.assertEqual(self.child.father, self.dad)

        self.mom.add_child(self.child)
        self.assertIn(self.child, self.mom.children)
        self.assertEqual(self.child.mother, self.mom)

    def test_add_child_error(self):
        self.dad.gender = Gender.UNKNOWN
        with self.assertRaises(RelatedPersonError) as context:
            self.dad.add_child(self.child)
        self.assertRegex(str(context.exception), "cannot add child.*with unknown gender")

        self.dad.gender = Gender.MALE
        self.child.gender = Gender.MALE
        self.child.set_father(self.dad)
        with self.assertRaises(RelatedPersonError) as context:
            self.child.add_child(self.dad)
        self.assertRegex(str(context.exception), "would create ancestor cycle")

        with self.assertRaises(RelatedPersonError) as context:
            self.child.add_child(self.child)
        self.assertRegex(str(context.exception), "cannot add him/herself as a child")

    def test_ancestor(self):
        mindepth = 0
        maxdepth = 1
        self.assertEqual(self.root_child.ancestors(mindepth, maxdepth),
                         {self.root_child, self.root_child.father, self.root_child.mother})

        mindepth = 1
        maxdepth = None
        self.assertEqual(self.root_child.ancestors(mindepth, maxdepth),
                         {self.root_child.father, self.root_child.mother})

    def test_ancestors_error(self):
        with self.assertRaises(RelatedPersonError) as context:
            self.root_child.ancestors(3, 2)
        self.assertRegex(str(context.exception), "max_depth.*cannot be less than min_depth")

    def test_parents(self):
        self.assertEqual(self.root_child.parents(), set(self.people[1:3]))

    def test_grandparents(self):
        check = {self.root_child.father.father, self.root_child.father.mother,
                 self.root_child.mother.father, self.root_child.mother.mother}
        self.assertEqual(self.root_child.grandparents(), check)

    def test_all_ancestors(self):
        self.assertEqual(self.root_child.all_ancestors(), set(self.people[1:]))

    def test_grandparents_and_earlier(self):
        all_grandparents = set(self.people).difference([self.root_child], self.root_child.parents())
        self.assertEqual(self.root_child.grandparents_and_earlier(), all_grandparents)


if __name__ == '__main__':
    unittest.main()