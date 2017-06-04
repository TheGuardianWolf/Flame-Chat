contoso.controller('overviewController', ['$scope', function($scope) {
  $scope.nextCoursework = { };
  $scope.taskList = Cache.toDos;
  $scope.courseList = Cache.enrolledCourses;

  $scope.getGrade = function(courseID) {
    var grade;
    for (var i = 0; i < Cache.enrollments.length; i++) {
      if (Cache.enrollments[i].CourseID === courseID) {
        thisCourseEnrollment = Cache.enrollments[i];
        grade = thisCourseEnrollment.Grade;
      }
    }
    if (!grade) {
      return 'Not Graded';
    }
    else {
      switch (parseInt(grade)) {
        case 0:
          return 'A';
        case 1:
          return 'B';
        case 2:
          return 'C';
        case 3:
          return 'D';
        case 4:
          return 'F';
        default:
          return 'Not Graded';
      }
    }
  };

  $scope.getPercentComplete = function (courseID){
    var thisCourseEnrollment;
    for (var i = 0; i < Cache.enrollments.length; i++) {
      if (Cache.enrollments[i].CourseID === courseID) {
        thisCourseEnrollment = Cache.enrollments[i];
        return thisCourseEnrollment.PercentComplete;
      }
    }
  };

}]);