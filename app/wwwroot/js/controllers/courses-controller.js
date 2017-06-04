contoso.controller('coursesController', ['$scope', function($scope) {
  var i;
  //build actions
  $scope.courses = Cache.courses;
  $scope.enrolledCourses = Cache.enrolledCourses;
  $scope.freeCourses = Cache.freeCourses;
  $scope.courseAssignments = {};
  $scope.courseTests = {};

  $scope.getPercentComplete = function (courseID){
    var thisCourseEnrollment;
    for (var i = 0; i < Cache.enrollments.length; i++) {
      if (Cache.enrollments[i].CourseID === courseID) {
        thisCourseEnrollment = Cache.enrollments[i];
        return thisCourseEnrollment.PercentComplete;
      }
    }
  };

  $scope.getCompletionInfo = function (courseID){
    var thisCourseEnrollment;
    for (var i = 0; i < Cache.enrollments.length; i++) {
      if (Cache.enrollments[i].CourseID === courseID) {
        thisCourseEnrollment = Cache.enrollments[i];
        return thisCourseEnrollment.CompletionInfo;
      }
    }
  };

  $scope.onClickChange = function(courseID) {
    $scope.changeCourse.courseID = courseID;
    for (var i = 0; i < Cache.enrollments.length; i++) {
      if (Cache.enrollments[i].CourseID === courseID) {
        $scope.changeCourse.enrollmentID = Cache.enrollments[i].ID;
        break;
      }
    }
    var dialog = $('#changeCourse').data('dialog');
    dialog.open();
  };

  $scope.changeCourse = {
    go : function() {
      if (!$scope.state.ajaxBusy) {
        $scope.state.ajaxBusy = true;
        var dialog = $('#changeCourse').data('dialog');
        var courseID = $scope.changeCourse.courseID;
        dialog.close();
        console.log($scope.changeCourse);
        var data = {
          "ID": $scope.changeCourse.enrollmentID,
          "CourseID": courseID,
          "StudentID": Cache.user.ID,
          "PercentComplete": $scope.changeCourse.completion,
          "Grade": $scope.changeCourse.grade
        };
        console.log(data.ID.toString());
        $scope.requests('PUT','Enrollments.' + data.ID.toString(), data).then(function(response) {
          console.log(response);
          var i;
          var updatedEnrollment = response.data;
          for (i = 0; i < Cache.enrollments.length; i++) {
            if (Cache.enrollments[i].CourseID === courseID) {
              Cache.enrollments[i].PercentComplete = $scope.changeCourse.completion;
              Cache.enrollments[i].Grade = $scope.changeCourse.grade;
              break;
            }
          }
          $scope.state.ajaxBusy = false;
          $.Notify({
            caption: 'Update complete',
            content: 'Course has been changed',
            type: 'success'
          });
        }, function(error) {
          $scope.state.ajaxBusy = false;
          console.log(error);
          $.Notify({
            caption: 'Error',
            content: 'An error has occured.',
            type: 'alert'
          });
        });
      }
      else {
        $.Notify({
          caption: 'Busy',
          content: 'Updating enrollments.',
          type: 'warning'
        });
      }
    },
    enrollmentID : 0,
    courseID : 0,
    grade : "",
    completion : 0,
  };



  $scope.dropCourse = function(courseID) {
    if (!$scope.state.ajaxBusy) {
      $scope.state.ajaxBusy = true;
      $.Notify({
        caption: 'Removing course',
        content: 'Please wait while the course is removed from your enrollments.',
        type: 'info'
      });
      var thisCourseEnrollment;
      var enrollmentIndex;
      for (var i = 0; i < Cache.enrollments.length; i++) {
        if (Cache.enrollments[i].CourseID === courseID) {
          enrollmentIndex = i;
          thisCourseEnrollment = Cache.enrollments[i];
        }
      }
      $scope.requests('DELETE', 'Enrollments.' + thisCourseEnrollment.ID).then(function successCallback(response) {
        $.Notify({
          caption: 'Update complete',
          content: 'Course has been removed.',
          type: 'Success'
        });
        $scope.state.ajaxBusy = false;
        var deletedCourse;

        for (var i = 0; i < $scope.enrolledCourses.length; i++) {
          if ($scope.enrolledCourses[i].ID === courseID) {
            deletedCourse = $scope.enrolledCourses[i];
            $scope.enrolledCourses.splice(i,1);
          }
        }
        $scope.freeCourses.push(deletedCourse);
        Cache.enrollments.splice(enrollmentIndex,1);
        Cache.enrolledCourseIDs.splice(Cache.enrolledCourseIDs.indexOf(courseID));
        $scope.counters.courses = Cache.enrolledCourses.length;
      }, function errorCallback(response) {
        $scope.state.ajaxBusy = false;
        $.Notify({
          caption: 'Error',
          content: 'An error has occured.',
          type: 'Alert'
        });
      });
    }
    else {
      $.Notify({
        caption: 'Busy',
        content: 'Updating enrollments.',
        type: 'warning'
      });
    }

  };

  $scope.enrollCourse = function(courseID) {
    if (!$scope.state.ajaxBusy) {
      $scope.state.ajaxBusy = true;
      $.Notify({
        caption: 'Enrolling in course',
        content: 'Please wait while the course is added to your enrollments.',
        type: 'info'
      });
      var thisCourseEnrollment = {
        "ID": 0,
        "CourseID": courseID,
        "StudentID": Cache.user.ID,
        "PercentComplete": "0",
        "Grade": undefined,
      };
      $scope.requests('POST', 'Enrollments', thisCourseEnrollment)
      .then(function successCallback(response) {
        $.Notify({
          caption: 'Update complete',
          content: 'Course has been added.',
          type: 'Success'
        });
        var newEnrollment = response.data;
        $scope.requests('GET', 'Enrollments')
        .then(function successCallback(response) {
          for (var i = 0; i < Cache.courses.length; i++) {
            if (Cache.courses[i].ID === courseID) {
              $scope.enrolledCourses.push(Cache.courses[i]);
              break;
            }
          }
          for (var j = 0; j < Cache.freeCourses.length; j++) {
            if (Cache.freeCourses[j].ID === courseID) {
              Cache.freeCourses.splice(j,1);
              break;
            }
          }
          Cache.enrollments.push(newEnrollment);
          Cache.enrolledCourseIDs.push(newEnrollment.courseID);
          $scope.counters.courses = Cache.enrolledCourses.length;
        },
        function errorCallback(response) {
          $scope.state.ajaxBusy = false;
          $.Notify({
            caption: 'Error',
            content: 'An error has occured.',
            type: 'Alert'
          });
        });
        $scope.state.ajaxBusy = false;
      }, function errorCallback(response) {
        $scope.state.ajaxBusy = false;
        $.Notify({
          caption: 'Error',
          content: 'An error has occured.',
          type: 'Alert'
        });
      });
    }
    else {
      $.Notify({
        caption: 'Busy',
        content: 'Updating enrollments.',
        type: 'warning'
      });
    }

  };

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

  $scope.hasCoursework = function(courseID, completionText) {
    if (!$scope.courseAssignments[courseID] && !$scope.courseTests[courseID] && !completionText) {
      return false;
    }
    return true;
  };

  for (i = 0; i < Cache.assignments.length; i++) {
    if ($scope.courseAssignments[Cache.assignments[i].CourseID] === undefined) {
      $scope.courseAssignments[Cache.assignments[i].CourseID] = [];
    }
    $scope.courseAssignments[Cache.assignments[i].CourseID].push(Cache.assignments[i]);
  }

  for (i = 0; i < Cache.tests.length; i++) {
    if ($scope.courseTests[Cache.tests[i].CourseID] === undefined) {
      $scope.courseTests[Cache.tests[i].CourseID] = [];
    }
    $scope.courseTests[Cache.tests[i].CourseID].push(Cache.tests[i]);
  }
}]);