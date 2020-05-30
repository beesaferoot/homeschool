import datetime

from homeschool.schools.models import GradeLevel
from homeschool.schools.tests.factories import SchoolYearFactory
from homeschool.test import TestCase


class TestCurrentSchoolYearView(TestCase):
    def test_unauthenticated_access(self):
        self.assertLoginRequired("schools:current_school_year")

    def test_get(self):
        user = self.make_user()
        school_year = SchoolYearFactory(school=user.school)

        with self.login(user):
            self.get_check_200("schools:current_school_year")

        assert school_year == self.get_context("schoolyear")

    def test_future_school_year(self):
        """Go to a future school year if there is no current one.

        The user may be new and have no currently active school year.
        It would be pretty lame to send them to the list
        when they may be building out their first school year.
        """
        user = self.make_user()
        today = user.get_local_today()
        school_year = SchoolYearFactory(
            school=user.school,
            start_date=today + datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=200),
        )

        with self.login(user):
            self.get_check_200("schools:current_school_year")

        assert school_year == self.get_context("schoolyear")

    def test_no_current_school_year(self):
        """With no current school year, the user sees the school year list page."""
        user = self.make_user()

        with self.login(user):
            response = self.get("schools:current_school_year")

        self.response_302(response)
        assert self.reverse("schools:school_year_list") in response.get("Location")

    def test_only_school_year_for_user(self):
        """A user may only view their own school years."""
        user = self.make_user()
        SchoolYearFactory()

        with self.login(user):
            response = self.get("schools:current_school_year")

        self.response_302(response)


class TestSchoolYearDetailView(TestCase):
    def test_unauthenticated_access(self):
        school_year = SchoolYearFactory()
        self.assertLoginRequired("schools:school_year_detail", uuid=school_year.uuid)

    def test_get(self):
        user = self.make_user()
        school_year = SchoolYearFactory(school=user.school)

        with self.login(user):
            self.get_check_200("schools:school_year_detail", uuid=school_year.uuid)

    def test_only_school_year_for_user(self):
        """A user may only view their own school years."""
        user = self.make_user()
        school_year = SchoolYearFactory()

        with self.login(user):
            response = self.get("schools:school_year_detail", uuid=school_year.uuid)

        self.response_404(response)


class TestSchoolYearListView(TestCase):
    def test_unauthenticated_access(self):
        self.assertLoginRequired("schools:school_year_list")

    def test_get(self):
        user = self.make_user()
        school_year = SchoolYearFactory(school=user.school)

        with self.login(user):
            self.get_check_200("schools:school_year_list")

        assert school_year in self.get_context("schoolyear_list")

    def test_only_school_year_for_user(self):
        """A user may only view their own school years."""
        user = self.make_user()
        school_year = SchoolYearFactory()

        with self.login(user):
            self.get("schools:school_year_list")

        assert school_year not in self.get_context("schoolyear_list")


class TestGradeLevelCreateView(TestCase):
    def test_unauthenticated_access(self):
        school_year = SchoolYearFactory()
        self.assertLoginRequired("schools:grade_level_create", uuid=school_year.uuid)

    def test_get(self):
        user = self.make_user()
        school_year = SchoolYearFactory(school=user.school)

        with self.login(user):
            self.get_check_200("schools:grade_level_create", uuid=school_year.uuid)

        assert school_year == self.get_context("school_year")

    def test_post(self):
        """A user can create a grade level for their school year."""
        user = self.make_user()
        school_year = SchoolYearFactory(school=user.school)
        data = {"school_year": str(school_year.id), "name": "3rd Grade"}

        with self.login(user):
            response = self.post(
                "schools:grade_level_create", uuid=school_year.uuid, data=data
            )

        grade_level = GradeLevel.objects.get(school_year=school_year)
        assert grade_level.name == "3rd Grade"
        self.response_302(response)
        assert response.get("Location") == self.reverse(
            "schools:school_year_detail", uuid=school_year.uuid
        )

    def test_not_found_for_other_school(self):
        """A user cannot add a grade level to another user's school year."""
        user = self.make_user()
        school_year = SchoolYearFactory()

        with self.login(user):
            response = self.get("schools:grade_level_create", uuid=school_year.uuid)

        self.response_404(response)
