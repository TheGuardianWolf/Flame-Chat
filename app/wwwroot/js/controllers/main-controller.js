flame.controller('mainController', [
    '$scope', 
    '$http', 
    '$location',
    'poller', 
    function ($scope, $http, $location, poller) {
        $scope.state = {
            loading: false,
            authenticated: false,
            sidebarCompact: true,
            activePath: ''
        };

        $scope.data = {
            currentUser: {
                username: '',
                password: ''
            },
            users: [],
            profiles: [],
            status: [],
            files: [],
            messages: []
        };

        $scope.goto = function(path) {
            $location.path(path);
            $scope.state.activePath = path;
        };

        if ($scope.state.authenticated === false) {
            $scope.goto('');
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
            if (args.length > 0) {
                args[0].ignoreLoadingBar = true;
            }
            else {
                args.push({
                    ignoreLoadingBar: true
                });
            }

            var request = poller.get(apiRoute([dataType, method]), {
                action: method,
                delay: delay,
                argumentsArray: args
            });
            request.promise.then(null, null, function(response) {
                $scope.data[dataType] = response.data;
            });
            return request;
        };

        var fetchConversations = function(delay) {
            var lastFetch = {
                messages: null,
                files: null
            };
            
            var fetchMessages = function() {
                return poller.get(apiRoute(['messages', 'get']), {
                    action: 'get',
                    delay: delay,
                    argumentsArray: function() {
                        var args = [{
                            ignoreLoadingBar: true
                        }];

                        if (lastFetch.messages !== null) {
                            args[0].params = {
                                since: lastFetch.messages
                            };
                        }

                        return args;
                    }
                });
            };
            
            var fetchFiles = function() {
                return poller.get(apiRoute(['files', 'get']), {
                    action: 'get',
                    delay: delay,
                    argumentsArray: function() {
                        var args = [{
                            ignoreLoadingBar: true
                        }];

                        if (lastFetch.files !== null) {
                            args[0].params = {
                                since: lastFetch.files
                            };
                        }

                        return args;
                    }
                });
            };

            var m = fetchMessages();
            m.promise.then(null, null, function(response) {
                if (lastFetch.messages !== null) {
                    $scope.data.messages.push.apply($scope.data.messages, response.data);
                }
                else {
                    $scope.data.messages = response.data;
                }
                lastFetch.messages = String(Date.now() / 1000);
            });

            var f = fetchFiles();
            f.promise.then(null, null, function(response) {
                if (lastFetch.files !== null) {
                    $scope.data.files.push.apply($scope.data.files, response.data);
                }
                else {
                    $scope.data.files = response.data;
                }
                lastFetch.files = String(Date.now() / 1000);
            });

            return [m, f];
        };

        var startCycles = function() {
            $scope.streamConnect();
            var userCycle = fetch('users', 'get', 5000, []);
            var profileCycle = fetch('profiles', 'get', 30000, []);
            var statusCycle = fetch('status', 'get', 5000, []);
            var conversationCycle = fetchConversations(5000);
        };

        $scope.startCycles = startCycles;
    }
]);