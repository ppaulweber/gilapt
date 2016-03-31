#   
#   Copyright (c) 2016 Philipp Paulweber
#   All rights reserved.
#   
#   Developed by: Philipp Paulweber
#                 https://github.com/ppaulweber/gilapt
#   
#   Permission is hereby granted, free of charge, to any person obtaining a 
#   copy of this software and associated documentation files (the "Software"), 
#   to deal with the Software without restriction, including without limitation 
#   the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#   and/or sell copies of the Software, and to permit persons to whom the 
#   Software is furnished to do so, subject to the following conditions:
#   
#   * Redistributions of source code must retain the above copyright 
#     notice, this list of conditions and the following disclaimers.
#   
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimers in the 
#     documentation and/or other materials provided with the distribution.
#   
#   * Neither the names of the copyright holders, nor the names of its 
#     contributors may be used to endorse or promote products derived from 
#     this Software without specific prior written permission.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
#   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#   CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
#   WITH THE SOFTWARE.
#   

import sys

sys.path.append( "./lib/requests" )
sys.path.append( "./lib/gitlab" )
sys.path.append( "./lib/org/py" )

import gitlab
import libOrg

if len( sys.argv ) != 4 :
    sys.stderr.write( "%s: error: provide a GitLab access token!\n" % sys.argv[0] )
    sys.exit(-1)


    
class gilapt(object):
    """GitLab Python Tool"""
    
    def __init__( self, host, token = "" ) :    
        self._git = gitlab.Gitlab( "https://%s" % host, token = token, verify_ssl = False )
        
        self._users   = None
        self._id2user = {}
        
        self._groups = None
        self._id2group = {}
        
        self._repos  = None
        self._id2repo = {}
    # end def
    
    def sync( self ) :
        self.getUsers( False )
        self.getGroups( False )
        self.getRepos( False )
    # end def

    
    ############################################################################
    # USER
    ############################################################################
    
    def getUsers( self, cache = True ) :
        if self._users is None or cache is False :
            self._users = []
            c = 1
            result = None
            while result is None or len( result ) != 0 :
                result = self._git.getusers( page=c )
                c = c + 1  
                for r in result :
                    self._users.append( r )
            
            self._id2user = {}
            for u in self._users :
                self._id2user[ u['id'] ] = u
            
        return self._users
    # end def
    
    def getUser( self, username_or_email, cache = True ) :
        result = self.getUsers( cache )

        users = []
        for r in result :
            if username_or_email in r['username'] \
            or username_or_email in r['email'] :
                users.append( r )
        
        if len( users ) == 0 or len( users ) > 1 :
            return None
        else :
            return users[ 0 ]
    # end def
    
    def _get_user_by_id( self, user_id, cache = True ) : 
        self.getUsers( cache )
        
        try :
            return self._id2user[ user_id ]
        except :
            return None
    # end def
    
    def hasUser( self, username_or_email, cache = True ) :
        result = self.getUser( username_or_email, cache )
        
        if result is None :
            return False
        else :
            return True
    # end def

    def addUser \
    ( self
    , fullname, username, password, email
    , projects_limit = None
    , can_create_group = None
    , confirm = None
    , admin = None
    , skype = None
    , linkedin = None
    , twitter = None
    , url = None
    , bio = None
    , ext = None
    , eid = None
    , epr = None
    ) :        
        params = {}
        if projects_limit is not None :
            params['projects_limit'] = projects_limit # Number of projects user can create
        else :
            params['projects_limit'] = 0
        
        if can_create_group is not None :
            params['can_create_group'] = can_create_group # User can create groups - true or false
        else :
            params['can_create_group'] = "false"
        
        if confirm is not None :
            params['confirm'] = confirm # Require confirmation - true (default) or false
        if admin is not None :
            params['admin'] = admin # User is admin - true or false (default)
        if skype is not None :
            params['skype'] = skype # Skype Account
        if linkedin is not None :
            params['linkedin'] = linkedin # LinkedIn Account
        if twitter is not None :
            params['twitter'] = twitter # Twitter Account
        if url is not None :
            params['website_url'] = url # Website URL
        if bio is not None :
            params['bio'] = bio # User's biography
        if ext is not None :
            params['external'] = ext # Flags the user as external - true or false(default)
        if eid is not None :
            params['extern_uid'] = eid # External UID
        if epr is not None :
            params['provider'] = epr # External Provider Name
        
        result = self._git.createuser( fullname, username, password, email, **params )
        return result
    # end def
    
    def dumpUsers( self, search = "", cache = True, stream = sys.stdout, seperator = ", ", startOfLine = "", endOfLine = "\n" ) :
        result = []
        result.append( { 'id': "ID", 'username' : "User Name", 'name' : "Full Name", 'email' : "Email" } )
        
        for u in self.getUsers( cache ) :
            if len( search ) == 0 \
            or search in u['username'] \
            or search in u['email'] :
                result.append( u )
        
        for r in result :
            stream.write( "%s%s%s%s%s%s%s%s%s" % \
            ( startOfLine
            , r['id'], seperator
            , r['username'], seperator
            , r['name'], seperator
            , r['email'], endOfLine
            ))
    # end def

    
    ############################################################################
    # GROUP
    ############################################################################
    
    def getGroups( self, cache = True ) :
        if self._groups is None or cache is False :        
            self._groups = []
            c = 1
            result = None
            while result is None or len( result ) != 0 :
                result = self._git.getgroups( page=c )
                c = c + 1  
                for r in result :
                    self._groups.append( r )

            self._id2group = {}
            for g in self._groups :
                self._id2group[ g['id'] ] = g
            
        return self._groups
    # end def
    
    def getGroup( self, groupname, cache = True ) :
        groups = self.getGroups( cache )
        for g in groups :
            if g[ "path" ] == groupname :
                return g
        return None
    # end def

    def _get_group_by_id( self, group_id, cache = True ) : 
        self.getGroups( cache )
        
        try :
            return self._id2group[ group_id ]
        except :
            return None
    # end def
    
    def hasGroup( self, groupname, cache = True ) :
        result = self.getGroup( groupname, cache )
        
        if result is None :
            return False
        else :
            return True
    # end def
    
    def dumpGroups( self, search = "", cache = True, stream = sys.stdout, seperator = ", ", startOfLine = "", endOfLine = "\n" ) :
        result = []
        result.append( { 'id': "ID", 'path' : "Group Name", 'description' : "Description" } )
        
        for g in self.getGroups( cache ) :
            if len( search ) == 0 or search in g['path'] :
                result.append( g )
        
        for r in result :
            stream.write( "%s%s%s%s%s%s%s" % \
            ( startOfLine
            , r['id'], seperator
            , r['path'], seperator
            , r['description'], endOfLine
            ))
    # end def
    
    
    ############################################################################
    # REPOSITORIES
    ############################################################################
    
    def getRepos( self, cache = True ) :
        if self._repos is None or cache is False :
            self._repos = []
            c = 1
            result = None
            while result is None or len( result ) != 0 :
                result = self._git.getprojectsall( page=c )
                c = c + 1
                for project in result :
                    self._repos.append( project )

            for r in self._repos :
                self._id2repo[ r['id'] ] = r
            
        return self._repos
    # end def

    def getRepo( self, name, cache = True ) :
        pass
    # end def
    
    def getRepo( self, repopath, cache = True ) :
        repos = self.getRepos( cache )
        for r in repos :
            if r[ "path_with_namespace" ] == repopath :
                return r
        return None
    # end def

    def _get_repo_by_id( self, repo_id, cache = True ) : 
        self.getRepos( cache )
        
        try :
            return self._id2repo[ repo_id ]
        except :
            return None
    # end def
    
    def hasRepo( self, repopath, cache = True ) :
        result = self.getRepo( repopath, cache )
        
        if result is None :
            return False
        else :
            return True
    # end def

    def addRepo( self ) :
        # git._git.createproject( "testproject2", namespace_id = 2, description = "lala project", snippets_enabled = "false", public = 0, merge_requests_enabled = "false" )
        pass
    # end def
    
    def dumpRepos( self, search = "", cache = True, stream = sys.stdout, seperator = ", ", startOfLine = "", endOfLine = "\n" ) :
        repos = self.getRepos( cache )
        
        result = []
        if len( search ) == 0 :
            result = repos
        else :
            for r in repos :
                if search in r[ "path_with_namespace" ] :
                    result.append( r )

        result = []
        result.append
        ( { 'id': "ID"
          , 'path_with_namespace' : "Repository Path"
          , 'description' : "Description"
          , 'public' : "Public"
          , 'namespace' : { 'owner_id' : None }
          }
        )
        
        for r in self.getRepos( cache ) :
            if len( search ) == 0 or search in r['path_with_namespace'] :
                result.append( r )
        
        for r in result :
            if r['namespace']['owner_id'] is None :
                owner = "Owner"
            else :
                owner = self._get_user_by_id( r['namespace']['owner_id'] )[ 'username' ]
            
            stream.write( "%s%s%s%s%s%s%s%s%s%s%s" % \
            ( startOfLine, r['id']
            , seperator,   r['path_with_namespace']
            , seperator,   r['description']
            , seperator,   r['public']
            , seperator,   owner
            , endOfLine
            ))
    # end def
    
    
    ############################################################################
    # BRANCHES
    ############################################################################

    def modBranch( self, repo, branch, protected ) :
        
        # git.protectbranch( repo_id, master_id )
        # git.unprotectbranch( repo_id, branch_id )
        
        pass 
    # end def

    def getBranch( self, repo, branch ) :
        
        # git.getbranch( repo_id, branch_id )
        # return False
        # return {} of branch info
        
        pass
    # end def

    def addBranch( self, repo, branch ) :
        
        # git.createbranch( repo_id, new_branch_id, fork_branch_id )
        
        pass
    # end def
    
    
    ############################################################################
    # FILES
    ############################################################################
    
    def addFile( self, repo, filepath, branch, data, commit_message, encoding = "text" ) :
        # encoding 'text' or 'base64'
        
        # git._git.createfile( 3, "README.md", "master", encoding, "# Hello Test Project", "Initial Commit" )
        # returns really True and False
        
        pass
    # end def
    
    def modFile( self, repo, filepath, branch, data, commit_message ) :
        # can also be used to create files with no care if it already exists or not :)
        
        # updatefile(self, project_id, file_path, branch_name, content, commit_message):
        pass
    # end def
    
    
# end class


git = gilapt( sys.argv[1], sys.argv[2] )

org = libOrg.libOrg( sys.argv[3] )

table = org.findFirstTable()

if table is None :
    sys.stderr.write( "%s: error: no org table found!\n" % sys.argv[0] )    
    sys.exit(-1)

def process_row( y, row ) :
    if row.columns[0] is None :
        return False

    #print row
    print row.columns[0]
# end def

org.iterateTable( table, None )
print "###########"

org.iterateTable( table, process_row )




def findGroup( path ) :
    c = 1
    result = None
    while result is None or len( result ) != 0 :
        result = git.getgroups( page=c )
        c = c + 1
        for group in result :
            if group["path"] == path :
                return group
    return None
# end def

def findProjects( group ) :
    projects = []
    c = 1
    result = None
    while result is None or len( result ) != 0 :
        result = git.getprojects( page=c )
        c = c + 1
        for project in result :
            if project["namespace"]["id"] == group["id"] :
                projects.append( project )
    return projects
# end def

def findProject( projects, name ) :
    for p in projects :
        if name == p["path"] :
            return p
    return None
# end def







# git.createproject( "test_repo_via_api", namespace_id = 32, description = "Test Repo Via API" )
# git.createfile( 61, "README.org", "master", "* Hello Test Repo\n\n\nThis is a README text.", "README\n\n* added README file" )
# git.updatefile( 61, "README.org", "master", "* Hello Test Repo\n\n\nThis is a README text, which is created via API.", "README\n\n* updated README file" )

# git.updatefile( 62, "README.md", "2016ss_swa_task0", "# Hello Test Repo=\n\n\nThis is a README text.\n", "README\n\n* update README file" )

def doit( name ) :
    group_id = "submission"
    
    group = findGroup( group_id )
    assert group is not None, "invalid group"

    namespace_id = group["id"]
    
    projects = findProjects( group )
    repo = findProject( projects, name )
    
    if repo is None :        
        print( "%s/%s: creating repository" % ( group_id, name ) )
        repo = git.createproject \
        ( name
        , namespace_id = namespace_id
        , description = "TODO Description"
        )
        assert isinstance( repo, dict ), "gitlab error"
    
    master_id = u"master"
    repo_id   = repo["id"]
    repo_path = repo["path_with_namespace"]

    print( "%s: found repository" % ( repo_path ) )
    
    if repo["default_branch"] is None :
        git.createfile \
        ( repo_id
        , "README.md"
        , "master"
        , "# Hello Test Repo\n\n\nThis is a README text. TODO :smiley:"
        , "Initial Commit\n"
        + "\n"
        + "* added README file"
        )
    
    print( "%s @ %s: set to protected" % ( repo_path, master_id ) )
    print git.protectbranch( repo_id, master_id )
    
    
    for i in range(1,5) :
        branch_id = u"2017ss_swa_task%s" % i
        
        branch = git.getbranch( repo_id, branch_id )
        
        if not isinstance( branch, dict ) :
            print( "%s @ %s: creating branch of '%s'" % ( repo_path, branch_id, master_id ) )
            branch = git.createbranch( repo_id, branch_id, master_id )
            assert isinstance( branch, dict ), "gitlab error"
        
        print( "%s @ %s: found branch" % ( repo_path, branch_id ) )
        
        print( "%s @ %s: set to unprotected" % ( repo_path, branch_id ) )
        print git.unprotectbranch( repo_id, branch_id )
# end def


import pdb; pdb.set_trace()
