"""
Tests for the lms_filter_generator
"""
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from student.tests.factories import UserFactory
from student.models import CourseEnrollment

from lms.lib.courseware_search.lms_filter_generator import LmsSearchFilterGenerator
from search.search_engine_base import SearchEngine

INDEX_NAME = "courseware_index"

class LmsSearchFilterGeneratorTestCase(ModuleStoreTestCase):
    """ Test case class to test search result processor """

    def build_courses(self):
        """
        Build up a course tree with multiple test courses
        """

        self.courses = [
            CourseFactory.create(
                org='ElasticsearchFiltering',
                course='ES101F',
                run='test_run',
                display_name='Elasticsearch Filtering test course',
            ),

            CourseFactory.create(
                org='FilterTest',
                course='FT101',
                run='test_run',
                display_name='FilterTest test course',
            )
        ]

    def setUp(self):
        super(LmsSearchFilterGeneratorTestCase, self).setUp()
        self.build_courses()
        self.user = UserFactory.create(username="jack", email="jack@fake.edx.org", password='test')
        for course in self.courses:
            CourseEnrollment.enroll(self.user, course.location.course_key)

    def test_course_id_not_provided(self):
        """
        Tests that we get the list of IDs of courses the user is enrolled in when the course ID is null or not provided
        """
        field_dictionary, filter_dictionary = LmsSearchFilterGenerator.generate_field_filters(user=self.user)

        self.assertTrue('start_date' in filter_dictionary)
        self.assertIn(unicode(self.courses[0].id), field_dictionary['course'])
        self.assertIn(unicode(self.courses[1].id), field_dictionary['course'])

        search_engine = SearchEngine.get_search_engine(index=INDEX_NAME)
        results = search_engine.search(
            query_string=None,
            field_dictionary=None,
            filter_dictionary=None)

    def test_course_id_provided(self):
        """
        Tests that we get the course ID when the course ID is provided
        """
        field_dictionary, filter_dictionary = LmsSearchFilterGenerator.generate_field_filters(
            user=self.user,
            course_id=unicode(self.courses[0].id)
        )

        self.assertTrue('start_date' in filter_dictionary)
        self.assertEqual(unicode(self.courses[0].id), field_dictionary['course'])
