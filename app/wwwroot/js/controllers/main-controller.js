flame.controller('mainController', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    var fetchUsers = function() {
        return $http({
            method: 'GET',
            url: apiRoute(['users', 'get'])
        })
        .then(
            function success(response) {
                console.log(response);
                if (response.data.constructor === Array) {
                    $scope.data.users = response.data;
                }
                else {
                    errorCode = parseInt(response.data);
                    $.Notify({
                        caption: 'Warning ' + response.data,
                        content: 'Unable to get user list, login server reports error.',
                        type: 'warning'
                    });
                }
            },
            function fail(response) {
                console.log(response);
                errorCode = parseInt(response.data);
                $.Notify({
                    caption: 'Warning ' + response.data,
                    content: 'Unable to get user list, local server unable to serve request.',
                    type: 'warning'
                });
            }
        );
    };

    $scope.state = {
        loading: false,
        authenticated: false,
        sidebarCompact: true,
        ajaxBusy: false,
    };

    $scope.data = {
        users: []
    };

    $scope.cycle = {
        fetchUsers : null
    };

    $scope.goto = function(path) {
        $location.path(path);
    };

    if ($scope.state.authenticated === false) {
        $location.url('');
    }

    $scope.toggleSidebar = function () {
        $scope.state.sidebarCompact = !$scope.state.sidebarCompact;
    };

    $scope.streamConnect = function() {
        console.log('Creating new eventSource');
        var eventSource = new EventSource(apiRoute(['auth', 'stream']));
        eventSource.addEventListener('message', function(e) {
            console.log(e);
        }, false);

        eventSource.addEventListener('open', function(e) {
            console.log(e);
        }, false);

        eventSource.addEventListener('error', function(e) {
            if (e.readyState == EventSource.CLOSED) {
                console.log(e);
            }
        }, false);
        return eventSource;
    };

    $scope.startCycles = function() {
        fetchUsers();
        $scope.cycle.fetchUsers = setInterval(
            function() {
                fetchUsers();
            }, 60000
        );
    };
}]);