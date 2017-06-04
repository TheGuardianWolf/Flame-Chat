contoso.controller('authController', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    var authenticate = function(username, password) {
        return $http({
            method: 'POST',
            url: [apiUrl, 'auth', 'login'].join('/') + '/',
            data: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(
            function success(response) {
                console.log(response)
                $.Notify({
                    caption: 'Success',
                    content: 'Logged into local server.',
                    type: 'success'
                });
            },
            function fail(response) {
                console.log(response)
                $.Notify({
                    caption: 'Error',
                    content: 'Unable to authenticate, local server does not have an authentication source.',
                    type: 'alert'
                });
            }
        );
    };

    $scope.login = {}

    $scope.login.data = {
        username: '',
        password: ''
    };

    $scope.login.submit = function() {
        authenticate($scope.login.data.username, $scope.login.data.password);
    };

    // $scope.login = {
    //     data: {
            
    //     },
    //     submit: function () {
    //         if ($scope.state.ajaxBusy) {
    //             return false;
    //         }
    //         $http({
    //             method: 'POST',
    //             url: 'https://university-contoso-api.azurewebsites.net/Token',
    //             data: $.param({
    //                 grant_type: 'password',
    //                 username: $scope.login.data.Email,
    //                 password: $scope.login.data.Password,
    //             })
    //         }).then(function successCallback(response) {
    //             $scope.state.loading = true;
    //             Cache.auth = response;
    //             Cache.auth.header = 'Bearer ' + response.data.access_token;
    //             $scope.requests('GET', 'Account.UserInfo')
    //                 .then(function successCallback(response) {
    //                     Cache.userAccount = response.data;
    //                     return $scope.requests('GET', 'Students');
    //                 }, function errorCallback(response) {
    //                     $.Notify({
    //                         caption: 'Error',
    //                         content: 'Cannot retrieve remote data.',
    //                         type: 'alert'
    //                     });
    //                 })
    //                 .then(function successCallback(response) {
    //                     if (response.data.length > 0) {
    //                         var foundUser = false;
    //                         for (var i = 0; i < response.data.length; i++) {
    //                             if (Cache.userAccount.ID === response.data[i].AuthID) {
    //                                 Cache.user = response.data[i];
    //                                 foundUser = true;
    //                                 break;
    //                             }
    //                         }
    //                         if (!foundUser) {
    //                             $.Notify({
    //                                 caption: 'Warning',
    //                                 content: 'You seem to be not registered but have a valid identity token, please try signing up again.',
    //                                 type: 'warning'
    //                             });
    //                         } else {
    //                             requestData().then(function successCallback(response) {}, function errorCallback(response) {
    //                                 console.log(response);
    //                                 $.Notify({
    //                                     caption: 'Error',
    //                                     content: 'Cannot retrieve remote data.',
    //                                     type: 'alert'
    //                                 });
    //                                 $scope.state.loading = false;
    //                             });
    //                         }
    //                     }
    //                 }, function errorCallback(response) {
    //                     console.log(response);
    //                     $.Notify({
    //                         caption: 'Cannot log in',
    //                         content: 'Credentials invalid.',
    //                         type: 'alert'
    //                     });
    //                     $scope.state.loading = false;
    //                 });
    //         }, function errorCallback(response) {
    //             console.log(response);
    //             $.Notify({
    //                 caption: 'Cannot log in',
    //                 content: 'Credentials invalid.',
    //                 type: 'alert'
    //             });
    //             $scope.state.loading = false;
    //         });
    //     }
    // };
}]);