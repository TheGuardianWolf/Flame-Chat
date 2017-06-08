flame.controller('conversationsController', ['$scope', '$q', 'poller', function($scope, $q, poller) {
    // TODO: Find some way of combining messages and files

    var fetchConversations = function(target) {
        var fetchMessages = function(user) {
            return poller.get(apiRoute([dataType, method]), {
                action: method.toUpperCase(),
                delay: delay,
                argumentsArray: args
            });
        };
        
        var fetchFiles = function(user) {
            return poller.get(apiRoute([dataType, method]), {
                action: method.toUpperCase(),
                delay: delay,
                argumentsArray: args
            });
        };

        $q.all([
            fetchMessages().promise, 
            fetchFiles().promise
        ])
        .then(function(results) {
            messages = results[0].data;
            files = results[0].data;
        });
    };

    var userConversations = {};
    $scope.selectedUser = null;
    $scope.selectedUserMessages = function(user) {
        return userMessages[$scope.selectedUser];
    };
    $scope.selectUser = function(user) {
        $scope.selectedUser = user;
    };

}]);