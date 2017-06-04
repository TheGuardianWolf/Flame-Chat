contoso.controller('authController', ['$scope', '$http', '$location', function($scope, $http, $location) {
  var requestData = function() {
    var request = $scope.requests('GET', 'Enrollments');
    request.then(function successCallback(response) {
      if (response.data.length > 0) {
        var relevantEnrollments = [];
        for (var i = 0; i < response.data.length; i++) {
          if (response.data[i].StudentID === Cache.user.ID) {
            relevantEnrollments.push(response.data[i]);
            Cache.enrolledCourseIDs.push(response.data[i].CourseID);
          }
        }
        Cache.enrollments = relevantEnrollments;
      }
      return $scope.requests('GET', 'Courses')
      .then(function successCallback(response) {
        if (response.data.length > 0) {
          for (var i = 0; i < response.data.length; i++) {
            if (Cache.enrolledCourseIDs.indexOf(response.data[i].ID) > -1) {
              Cache.enrolledCourses.push(response.data[i]);
            }
            else {
              Cache.freeCourses.push(response.data[i]);
            }
          }
          Cache.courses = copy(response.data);
        }
        return $scope.requests('GET', 'Tests')
        .then(function successCallback(response) {
          if (response.data.length > 0) {
            Cache.tests = copy(response.data);
          }
          return $scope.requests('GET', 'Assignments')
          .then(function successCallback(response) {
            if (response.data.length > 0) {
              Cache.assignments = copy(response.data);
            }
            return $scope.requests('GET', 'AssignmentFiles')
            .then(function successCallback(response) {
              if (response.data.length > 0) {
                for (var i = 0; i< response.data.length; i++) {
                  if (response.data[i].StudentID === Cache.user.ID) {
                    Cache.assignments[response.data[i].AssignmentID] = {};
                    Cache.assignments[response.data[i].AssignmentID].link = response.data[i];
                  }
                }
                Cache.assignmentFiles = relevantFiles;
              }
              return $scope.requests('GET', 'ToDos')
              .then(function successCallback(response) {
                if (response.data.length > 0) {
                  for (var i = 0; i < response.data.length; i++) {
                    if (response.data[i].StudentID === Cache.user.ID) {
                      Cache.toDos.push(response.data[i]);
                    }
                  }
                }
                $scope.state.authenticated = true;
                $scope.counters.tasks = Cache.toDos.length;
                $scope.counters.courses = Cache.enrolledCourses.length;
                $location.url('overview');
                $scope.state.loading = false;
              }, function errorCallback(response) {
                console.log(response);
                alert(error);
              });
            }, function errorCallback(response) {
              console.log(response);
              alert(error);
              $scope.state.loading = false;
            });
          }, function errorCallback(response) {
            console.log(response);
            alert(error);
            $scope.state.loading = false;
          });
        }, function errorCallback(response) {
          console.log(response);
          alert(error);
          $scope.state.loading = false;
        });
      }, function errorCallback(response) {
        console.log(response);
        alert(error);
        $scope.state.loading = false;
      });
    }, function errorCallback(response) {
      console.log(response);
      alert(error);
      $scope.state.loading = false;
    });
    return request;
  };

  $scope.login = {
    show: true,
    data : {
      "Email" : "",
      "Password" : "",
    },
    submit : function() {
      if ($scope.state.ajaxBusy) {

        return false;
      }
      $http({
        method: 'POST',
        url: 'https://university-contoso-api.azurewebsites.net/Token',
        data: $.param({
          grant_type : 'password',
          username : $scope.login.data.Email,
          password : $scope.login.data.Password,
        })
      }).then(function successCallback(response) {
        $scope.state.loading = true;
        Cache.auth = response;
        Cache.auth.header = 'Bearer ' + response.data.access_token;
        $scope.requests('GET', 'Account.UserInfo')
        .then(function successCallback(response) {
          Cache.userAccount = response.data;
          return $scope.requests('GET', 'Students');
        }, function errorCallback(response) {
          $.Notify({
            caption: 'Error',
            content: 'Cannot retrieve remote data.',
            type: 'alert'
          });
        })
        .then(function successCallback(response) {
          if (response.data.length > 0) {
            var foundUser = false;
            for (var i=0; i < response.data.length; i++) {
              if (Cache.userAccount.ID === response.data[i].AuthID) {
                Cache.user = response.data[i];
                foundUser = true;
                break;
              }
            }
            if (!foundUser) {
              $.Notify({
                caption: 'Warning',
                content: 'You seem to be not registered but have a valid identity token, please try signing up again.',
                type: 'warning'
              });
            }
            else {
              requestData().then(function successCallback(response) {
              }, function errorCallback(response) {
                console.log(response);
                $.Notify({
                  caption: 'Error',
                  content: 'Cannot retrieve remote data.',
                  type: 'alert'
                });
                $scope.state.loading = false;
              });
            }
          }
        }, function errorCallback(response) {
          console.log(response);
          $.Notify({
            caption: 'Cannot log in',
            content: 'Credentials invalid.',
            type: 'alert'
          });
          $scope.state.loading = false;
        });
      }, function errorCallback(response) {
        console.log(response);
        $.Notify({
          caption: 'Cannot log in',
          content: 'Credentials invalid.',
          type: 'alert'
        });
        $scope.state.loading = false;
      });
    }
  };

  $scope.signup = {
    data : {
      "Email" : "",
      "Password" : "",
      "ConfirmPassword" : "",
      "FirstName" : "",
      "LastName" : "",
    },
    submit : function() {
      console.log($scope.signup.data);
      if ($scope.state.ajaxBusy) {
        return false;
      }
      if ($scope.signup.data.Password === $scope.signup.data.ConfirmPassword) {
        $scope.state.ajaxBusy = true;
        $http({
          method: 'POST',
          url: 'https://university-contoso-api.azurewebsites.net/api/Account/Register',
          data: {
            "Email": $scope.signup.data.Email,
            "Password": $scope.signup.data.Password,
            "ConfirmPassword": $scope.signup.data.ConfirmPassword}
        })
        .then(function successCallback(response) {
          return $http({
            method: 'POST',
            url: 'https://university-contoso-api.azurewebsites.net/Token',
            data: $.param({
              grant_type : 'password',
              username : $scope.signup.data.Email,
              password : $scope.signup.data.Password,
            })
          });
        }, function(error) {
          $.Notify({
            caption: 'Error',
            content: 'Unable to process auth',
            type: 'alert'
          });
        })
        .then(function(response) {
          Cache.auth = response;
          Cache.auth.header = 'Bearer ' + response.data.access_token;
          return $scope.requests('GET', 'Account.UserInfo');
        }, function(error) {

        })
        .then(function(response) {
          Cache.userAccount = response.data;
          return $http({
            method: 'POST',
            url: 'https://university-contoso-api.azurewebsites.net/api/Students',
            data: {
              "ID": 0,
              "AuthID": Cache.userAccount.ID,
              "FirstName": $scope.signup.data.FirstName,
              "LastName": $scope.signup.data.LastName,
              "EnrollmentDate": new Date().toMysqlFormat(),}
          });
        }, function(error) {
          $.Notify({
            caption: 'Error',
            content: 'Unable to process auth',
            type: 'alert'
          });
        })
        .then(function(response) {
          $scope.state.ajaxBusy = false;
          $scope.login.show = true;
          $.Notify({
            caption: 'Registered',
            content: 'Please log in now.',
            type: 'success'
          });
        }, function(error) {
          $.Notify({
            caption: 'Error',
            content: 'Unable to process registration',
            type: 'alert'
          });
        });
      }
      else {
        $.Notify({
        caption: 'Error',
        content: 'Passwords do not match.',
        type: 'alert'
        });
      }
    }
  };
}]);