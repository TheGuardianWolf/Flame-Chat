flame.controller('conversationsController', ['$scope', '$q', 'poller', function($scope, $q, poller) {
    // Create view models for templating
    $scope.showContent = function() {
        return $scope.selectedModel !== null;
    }
    $scope.selectedModel = null;
    $scope.selectModel = function(model) {
        var filter = function(obj) {
            return obj.sender == model.username || obj.destination == model.username;
        };

        var content = $scope.data.messages
        .filter(relatedFilter)
        .forEach(function(message) {
            message.ngId = 'm' + String(message.id);
        })
        .concat(
            $scope.data.files
            .filter(relatedFilter)
            .forEach(function(file) {
                file.ngId = 'f' + String(file.id);
                file.href = 'data:' + file.content_type +  ';base64,' + file.file;
            })
        )
        .sort(function(a, b) {
            return a.stamp - b.stamp;
        });

        $scope = selectedModel = {
            model: model,
            content: content
        };
    };

    $scope.listView = function() {
        var category = function(branch) {
            var models = $scope.data.users[branch]
            .map(function(user) {
                var userEntry = {
                    id: user.id,
                    displayName: user.username,
                    username: user.username,
                    picture: '/img/user-pic-placeholder.png',
                    status: 'Unknown',
                    alert: false
                };

                if (typeof $scope.data.status[user.username] !== 'undefined') {
                    userEntry.status = capitalize($scope.data.status[user.username]);
                }
                
                var profile = $scope.data.profiles.filter(function(profile) {
                    return profile.userId == user.id;
                });

                if (profile.length > 0) {
                    if (typeof profile[0].fullname !== 'undefined') {
                        userEntry.displayName = profile[0].fullname;
                    }
                    if (typeof profile[0].picture !== 'undefined') {
                        userEntry.picture = profile[0].picture;
                    }
                }

                return userEntry;
            });
        };
        return [
            {
                title: 'Reachable',
                models: category('reachable')
            },
            {
                title: 'Unreachable',
                models: category('unreachable')
            },
            {
                title: 'Unknown',
                models: category('unknown')
            }
        ];
    };
}]);