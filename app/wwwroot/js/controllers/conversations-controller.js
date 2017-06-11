flame.controller('conversationsController', ['$scope', '$http', function($scope, $http) {
    // Create view models for templating
    var updateContentModel = function() {
        model = $scope.selectedModel;
        if (model !== null) {
            var convoFilter = function(obj) {
                return obj.sender == model.username || obj.destination == model.username;
            };

            var content = $scope.data.messages
            .filter(convoFilter)
            .map(function(message) {
                message.ngId = 'm' + String(message.id);
                message.type = 'message';
                return message;
            })
            .concat(
                $scope.data.files
                .filter(convoFilter)
                .map(function(file) {
                    file.ngId = 'f' + String(file.id);
                    file.type = 'file';
                    file.href = 'data:' + file.content_type +  ';base64,' + file.file;
                    return file;
                })
            )
            .sort(function(a, b) {
                return a.stamp - b.stamp;
            });

            $scope.contentModel = content;
            console.log(content);
        }
    };
    $scope.showContent = function() {
        return $scope.contentModel !== null;
    };
    $scope.contentModel = null;
    $scope.selectedModel = null;
    $scope.selectListModel = function(model) {
        $scope.selectedModel = model;
        updateContentModel();
    };

    var updateCategoryModels = function(branch) {
        if (typeof $scope.data.users[branch] === 'undefined') {
            return [];
        }

        return $scope.data.users[branch]
        .map(function(user) {
            var userEntry = {
                id: user.id,
                displayName: user.username,
                username: user.username,
                picture: '/img/user-pic-placeholder.png',
                position: 'Unknown',
                description: 'Unknown',
                location: 'Unknown',
                status: 'Unknown',
                alert: false
            };

            if (branch === 'unknown') {
                userEntry.status = 'Offline';
            }

            if (typeof $scope.data.status[user.username] !== 'undefined') {
                userEntry.status = capitalize($scope.data.status[user.username]);
            }

            
            var profile = $scope.data.profiles.filter(function(profile) {
                return profile.userId === user.id;
            });

            if (profile.length > 0) {
                if (typeof profile[0].fullname !== 'undefined') {
                    userEntry.displayName = profile[0].fullname;
                }
                if (typeof profile[0].picture !== 'undefined') {
                    userEntry.picture = profile[0].picture;
                }
                if (typeof profile[0].description !== 'undefined') {
                    userEntry.description = profile[0].description;
                }
                if (typeof profile[0].location !== 'undefined') {
                    userEntry.location = profile[0].location;
                }
                if (typeof profile[0].position !== 'undefined') {
                    userEntry.position = profile[0].position;
                }
            }

            return userEntry;
        })
        .filter(function(user) {
            return user.username !== $scope.data.currentUser.username;
        })
        .sort(function(a, b) {
            if (a.username < b.username) {
                return -1;
            }
            else if (a.username > b.username) {
                return 1;
            }
            else {
                return 0;
            }
        });
    };

    $scope.listView = [
        {
            title: 'Reachable',
            models: []
        },
        {
            title: 'Unreachable',
            models: []
        },
        {
            title: 'Unknown',
            models: []
        }
    ];

    var updateListView = function(newValue, oldValue) {
        $scope.listView.forEach(function(listViewCategory) {
            listViewCategory.models = updateCategoryModels(
                listViewCategory.title.toLowerCase()
            );
        });
    };

    $scope.$watch('data.users', updateListView);
    $scope.$watch('data.profiles', updateListView);
    $scope.$watch('data.status', updateListView);
    $scope.$watch('data.messages', updateContentModel);
    $scope.$watch('data.files', updateContentModel);

    $scope.entry = {
        message: '',
        file: ''
    };

    var sendMessage = function() {
        var destination = $scope.selectedModel.model.username;
        var request = $http({
            method: 'POST',
            url: apiRoute(['messages', 'post']),
            data: JSON.stringify({
                destination: destination,
                message: $scope.entry.message
            })
        });
        $scope.entry.message = '';
    };
    $scope.sendMessage = sendMessage;

    $scope.$watch('entry.file', function() {
        if ($scope.entry.file) {
            sendFile();
        }
    });

    var sendFile = function() {
        var file = $scope.entry.file;
        var destination = $scope.selectedModel.model.username;
        var reader = new FileReader();
        
        reader.readAsDataURL(file);
        reader.addEventListener('load', function() {
            var dataURL = reader.result;
            var base64 = dataURL.replace(/^data:.*;base64,/, '');

            var request = $http({
                method: 'POST',
                url: apiRoute(['files', 'post']),
                data: JSON.stringify({
                    destination: destination,
                    filename: file.name,
                    file: base64,
                    content_type: file.type
                })
            });
            $scope.entry.message = '';
            return request;
        }, false);
    };

    $scope.insertEmote = function(event) {
        $scope.entry.message += event.target.innerText;
    };
}]);