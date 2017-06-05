import cherrypy
from datetime import datetime
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.ProfileModel import Profile
from json import loads, dumps

class ProfilesController(__Controller):
    def __init__(self, services):
         super(ProfilesController, self).__init__(services)

    def updateTable(self, profileList):
        conditionList = []
        for profile in profileList:
            conditionList.append('username=' + self.DS.queryFormat(profile.username))
        modelsList = [Profile] * len(conditionList)
        q = self.DS.selectMany(modelsList, conditionList)

        insertions = []
        updates = []
        updatesConditions = []

        for i, results in enumerate(q):
            if len(results) == 0:
                insertions.append(profileList[i])
            else:
                for dbEntry in results:
                    if not dbEntry == profileList[i]:
                        profileList[i].id = dbEntry.id
                        updates.append(profileList[i])
                        updatesConditions.append('id=' + self.DS.queryFormat(dbUser.id))

        self.DS.insertMany(insertions)
        self.DS.updateMany(updates, updatesConditions)

    def userProfileQuery(self):
        self.MS.data['lastUserProfileQuery'] = datetime.utcnow()
        return (0, 'Active user data updated')
        
        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        if not streamEnabled:
            if (self.MS.data['lastUserListRefresh'] - currentTime).seconds > 10:
                self.dynamicRefreshActiveUsers(cherrypy.session['username'], cherrypy.session['passhash'])
            if (self.MS.data['lastUserInfoQuery'] - currentTime).seconds > 10:
                self.queryActiveUsers()


