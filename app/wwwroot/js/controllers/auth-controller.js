flame.controller('authController', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    var authenticate = function(username, password) {
        $scope.state.loading = true;
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
                console.log(response);
                $scope.state.loading = false;
                errorCode = parseInt(reponse.data);
                if (errorCode === 0) {
                    $.Notify({
                        caption: 'Success',
                        content: 'Logged into local server.',
                        type: 'success'
                    });
                    $scope.state.authenticated = 'server';
                }
                else if (errorCode === -1 || errorCode === -2) {
                    $.Notify({
                        caption: 'Warning',
                        content: 'Locally authenticated, login server may be unavailable.',
                        type: 'warning'
                    });
                    $scope.state.authenticated = 'local';
                }
                else {
                    $.Notify({
                        caption: 'Error ' + response.data,
                        content: 'Unable to authenticate, login server reports error.',
                        type: 'alert'
                    });
                }

                if (['server', 'local'].includes($scope.state.authenticated)) {
                    $location.path('conversations');
                }
            },
            function fail(response) {
                console.log(response);
                $scope.state.loading = false;
                $.Notify({
                    caption: 'Error',
                    content: 'Unable to authenticate, local server does not have an authentication source.',
                    type: 'alert'
                });
            }
        );
    };

    $scope.login = {};

    $scope.login.data = {
        username: '',
        password: ''
    };

    $scope.login.submit = function() {
        authenticate($scope.login.data.username, $scope.login.data.password);
    };
}]);