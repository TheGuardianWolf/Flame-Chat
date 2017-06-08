flame.controller('authController', ['$scope', '$http', '$location', 'poller', function ($scope, $http, $location, poller) {
    var authenticate = function(username, password) {
        $scope.state.loading = true;
        return $http({
            method: 'POST',
            url: apiRoute(['auth', 'login']),
            data: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(
            function success(response) {
                errorCode = parseInt(response.data);
                if (errorCode === 0) {
                    $.Notify({
                        caption: 'Success',
                        content: 'Logged into local server.',
                        type: 'success'
                    });
                    $scope.state.authenticated = true;
                }
                else if (errorCode === -1 || errorCode === -2) {
                    $.Notify({
                        caption: 'Warning',
                        content: 'Locally authenticated, login server may be unavailable.',
                        type: 'warning'
                    });
                    $scope.state.authenticated = true;
                }
                else {
                    $.Notify({
                        caption: 'Error ' + response.data,
                        content: 'Unable to authenticate, login server reports error.',
                        type: 'alert'
                    });
                }

                if ($scope.state.authenticated) {
                    afterAuthenticate();
                }
                $scope.state.loading = false;
            },
            function fail(response) {
                $.Notify({
                    caption: 'Error',
                    content: 'Unable to authenticate, local server does not have an authentication source.',
                    type: 'alert'
                });
                $scope.state.loading = false;
            }
        );
    };

    var afterAuthenticate = function() {
        $scope.goto('conversations');
        // $scope.streamConnect();
        // $scope.startCycles();
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