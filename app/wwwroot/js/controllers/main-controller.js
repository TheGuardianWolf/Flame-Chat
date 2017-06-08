flame.controller('mainController', [
    '$scope', 
    '$http', 
    '$location', 
    '$resource', 
    'poller', 
    function ($scope, $http, $location, $resource, poller) {
        $scope.state = {
            loading: false,
            authenticated: false,
            sidebarCompact: true
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
            var eventSource = new EventSource(apiRoute(['stream']));
            eventSource.addEventListener('message', function(e) {
                console.log(e);
            }, false);

            eventSource.addEventListener('open', function(e) {
                console.log(e);
            }, false);

            eventSource.addEventListener('error', function(e) {
                console.log(e);
            }, false);
            return eventSource;
        };

        var fetch = function(dataType, method, delay, args) {
            var request = poller.get(apiRoute([dataType, method]), {
                action: method.toUpperCase(),
                delay: delay,
                argumentsArray: args
            });
            request.promise.then(null, null, function(response) {
                console.log(response);
                $scope.data[dataType] = response.data;
            });
            return request;
        };

        var startCycles = function() {
            fetchUsers = fetch('users', 'get', 5000, []);
            fetchProfiles = fetch('profiles', 'get', 5000, []);
            fetchStatus = fetch('status', 'get', 5000, []);
        };
    }
]);