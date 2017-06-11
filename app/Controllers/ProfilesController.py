import cherrypy
from datetime import datetime
from multiprocessing.pool import ThreadPool
from app import Globals
from app.Controllers.__Controller import __Controller
from app.Models.ProfileModel import Profile
from app.Models.UserModel import User
from json import loads, dumps

class ProfilesController(__Controller):
    def __init__(self, services):
         super(ProfilesController, self).__init__(services)

    def updateTable(self, profileList):
        conditionList = []
        for profile in profileList:
            conditionList.append('userId=' + self.DS.queryFormat(profile.userId))
        modelsList = [Profile] * len(conditionList)
        q = self.DS.selectMany(modelsList, conditionList)

        insertions = []
        updates = []
        updatesConditions = []

        for i, results in enumerate(q):
            if len(results) == 0:
                profileList[i].id = None;
                insertions.append(profileList[i])
            else:
                for dbEntry in results:
                    if not dbEntry == profileList[i]:
                        profileList[i].id = dbEntry.id
                        updates.append(profileList[i])

        self.DS.insertMany(insertions)
        self.DS.updateMany(updates)

    def userProfileQuery(self, username):
        self.MS.data['lastUserProfileQuery'] = datetime.utcnow()
        try:
            profileQueryList = self.MS.data['reachableUsers']
        except KeyError:
            profileQueryList = []

        pool = ThreadPool(processes=50)
        def getProfile(user):
            # Don't query for profiles at this server
            if user.ip == self.LS.ip:
                return (user, None)
            else:
                payload = {
                    'profile_username': user.username,
                    'sender': username
                }

                (status, response) = self.RS.post('http://' + str(user.ip) + ':' + str(user.port), '/getProfile', payload, timeout=5)

                if user.username == 'efon102':
                    cherrypy.log.error(unicode(response))

                if status == 200:
                    try:
                        return (user, loads(response.read()))
                    except (KeyError, TypeError, ValueError):
                        return (user, None)
                else:
                    return (user, None)

        responses = pool.map(getProfile, profileQueryList)

        profileList = []

        
        for response in responses:
            if response is not None:
                (user, profile) = response
                if profile is not None:
                    try:
                        model = Profile.deserialize(profile)
                        model.userId = user.id
                        profileList.append(model)
                    except TypeError:
                        pass

        self.updateTable(profileList)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            streamEnabled = cherrypy.session['streamEnabled']
        except KeyError:
            streamEnabled = False

        if not streamEnabled:
            username = cherrypy.session['username']
            cherrypy.session.release_lock()
            if self.checkTiming(self.MS.data, 'lastUserProfileQuery', 60):
                self.userProfileQuery(username)

        profiles = self.DS.select(Profile)

        responseObj = []

        for profile in profiles:
            responseObj.append(profile.serialize())

        return responseObj

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def post(self):
        if (cherrypy.request.remote.ip != '127.0.0.1'):
            raise cherrypy.HTTPError(403, 'You don\'t have permission to access /local/ on this server.')
        if not self.isAuthenticated():
            raise cherrypy.HTTPError(403, 'User not authenticated')

        try:
            request = cherrypy.request.json
        except AttributeError:
            raise cherrypy.HTTPError(400, 'JSON payload not sent.')

        if not self.checkObjectKeys(request, ['fullname', 'position', 'description', 'location', 'picture']):
            raise cherrypy.HTTPError(400, 'Missing required parameters.')

        # Get user id of posting user
        q = self.DS.select(User, 'username=' + self.DS.queryFormat(cherrypy.session['username']))

        try:
            user = q[0]
        except IndexError:
            raise cherrypy.HTTPError(500, 'Authorised user not in database.')

        # Add new entry for profile or update
        model = Profile.deserialize(request)
        model.userId = user.id
        self.updateTable([model])

        return
