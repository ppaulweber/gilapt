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

import os
import sys

sys.path.append( os.path.join( os.path.dirname( __file__ ), "lib", "requests" ) )
sys.path.append( os.path.join( os.path.dirname( __file__ ), "lib", "gitlab" ) )
sys.path.append( os.path.join( os.path.dirname( __file__ ), "lib", "org", "py" ) )

import gitlab
import libOrg

if len( sys.argv ) != 4 :
    sys.stderr.write( "%s: error: provide a GitLab access token!\n" % sys.argv[0] )
    sys.exit(-1)


    
class gilapt(object):
    """GitLab Python Tool"""
    
    def __init__( self, host, token = "", verify_ssl = True ) :
        self._git = gitlab.Gitlab( "https://%s" % host, token = token, verify_ssl = verify_ssl )
        
        self._users   = None
        self._id2user = {}
        
        self._groups = None
        self._id2group = {}
        
        self._namespaces = None
        self._id2namespace = {}
        
        self._repos  = None
        self._id2repo = {}
    # end def
    
    def sync( self ) :
        self.getUsers( False )
        self.getGroups( False )
        self.getNamespaces( False )
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
        
    def getUserID( self, username_or_email, cache = True ) :
        result = self.getUser( username_or_email, cache )
        assert result is not None, "user does not exist!"
        return result['id']
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

    def modUser( self, username_or_email, username = None, fullname = None, ext = None ) :
        uid = self.getUserID( username_or_email )
        
        params = {}
        if username is not None :
            params['username'] = username
        if fullname is not None :
            params['name'] = fullname
        if ext is not None :
            if ext is True :
                params['external'] = "true"
            elif ext is False :
                params['external'] = "false"
        
        self._git.edituser( uid, **params )
    # end def
    
    def dumpUsers( self, search = "", cache = True, stream = sys.stdout, seperator = ", ", startOfLine = "", endOfLine = "\n" ) :
        result = []
        
        for u in self.getUsers( cache ) :
            if len( search ) == 0 \
            or search in u['username'] \
            or search in u['email'] :
                result.append( u )

        result.append( { 'id': "ID", 'username' : "User Name", 'name' : "Full Name", 'email' : "Email" } )
        
        for r in result[::-1] :
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
    # NAMESPACES
    ############################################################################
    
    def getNamespaces( self, cache = True ) :
        if self._namespaces is None or cache is False :
            self._namespaces = []
            c = 1
            result = None
            while result is None or len( result ) != 0 :
                result = self._git.getnamespaces( page=c )
                c = c + 1
                for ns in result :
                    self._namespaces.append( ns )
            
            for ns in self._namespaces :
                self._id2namespace[ ns['id'] ] = ns
            
        return self._namespaces
    # end def

    def getNamespace( self, namespace, cache = True ) :
        result = self.getNamespaces( cache )
        for r in result :
            if r[ "path" ] == namespace :
                return r
        return None
    # end def
    
    def hasNamespace( self, namespace, cache = True ) :
        result = self.getNamespace( namespace, cache )

        if result is None :
            return False
        else :
            return True
    # end def

    def dumpNamespaces( self, search = "", cache = True, stream = sys.stdout, seperator = ", ", startOfLine = "", endOfLine = "\n" ) :
        result = []
        result.append( { 'id': "ID", 'path' : "Namespace", 'kind' : "Kind" } )
        
        for g in self.getNamespaces( cache ) :
            if len( search ) == 0 or search in g['path'] :
                result.append( g )
        
        for r in result :
            stream.write( "%s%s%s%s%s%s%s" % \
            ( startOfLine
            , r['id'], seperator
            , r['kind'], seperator
            , r['path'], endOfLine
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
    
    def getRepo( self, repopath, cache = True ) :
        repos = self.getRepos( cache )
        for r in repos :
            if r[ "path_with_namespace" ] == repopath :
                return r
        return None
    # end def
    
    def getRepoID( self, repopath, cache = True ) :
        result = self.getRepo( repopath, cache )
        assert result is not None, "repo does not exist!"
        return result['id']
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

    def addRepo \
    ( self
    , name
    , namespace
    , description
    , public = False
    , issues = True
    , snippets = True
    , merge = True
    , wiki = True
    , builds = True
    ) :
        params = {}        
        params['namespace_id'] = self.getNamespace( namespace )['id']
        params['description']  = description
        
        if public :
            params['public'] = "true"
        else :
            params['public'] = "false"

        if issues :
            params['issues_enabled'] = "true"
        else :
            params['issues_enabled'] = "false"
            
        if snippets :
            params['snippets_enabled'] = "true"
        else :
            params['snippets_enabled'] = "false"

        if merge :
            params['merge_requests_enabled'] = "true"
        else :
            params['merge_requests_enabled'] = "false"

        if wiki :
            params['wiki_enabled'] = "true"
        else :
            params['wiki_enabled'] = "false"

        if builds :
            params['builds_enabled'] = "true"
        else :
            params['builds_enabled'] = "false"
        
        self._git.createproject( name, **params )
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

    def modBranch( self, repopath, branch, protect, cache = True ) :
        if not self.hasBranch( repopath, branch, cache ) :
            assert False, "repo branch does not exist!"

        uid = self.getRepoID( repopath, cache )
        
        if protect :
            git.protectbranch( uid, branch )
        else :
            git.unprotectbranch( uid, branch )
    # end def
    
    def getBranch( self, repopath, branch, cache = True ) :
        uid = self.getRepoID( repopath, cache )
    
        result = self._git.getbranch( uid, branch )
        if isinstance( result, dict ) :
            return result
        else :
            return None
    # end def
    
    def hasBranch( self, repopath, branch, cache = True ) :
        result = self.getBranch( repopath, branch, cache )
        
        if result is None :
            return False
        else :
            return True
    # end def
    
    def addBranch( self, repopath, new_branch, old_branch, cache = True ) :
        if self.hasBranch( repopath, new_branch, cache ) :
            assert False, "repo 'new_branch' already exists!"
        if not self.hasBranch( repopath, old_branch, cache ) :
            assert False, "repo 'old_branch' does not exist!"
        
        uid = self.getRepoID( repopath, cache )
        
        git.createbranch( uid, new_branch, old_branch )
    # end def
    
    
    ############################################################################
    # FILES
    ############################################################################

    def getFile( self, repopath, branch, filepath, cache = True ) :
        uid = self.getRepoID( repopath, cache )
        if not self.hasBranch( repopath, branch, cache ) :
            assert False, "repo branch does not exist!"

        result = git._git.getfile( uid, filepath, "master2" )
        if isinstance( result, dict ) :
            return result
        else :
            return None
    # end def

    def hasFile( self, repopath, branch, filepath, cache = True ) :
        result = self.getFile( repopath, branch, filepath, cache )
        
        if result is None :
            return False
        else :
            return True
    # end def
    
    def addFile( self, repopath, branch, filepath, data, commit_message, encoding = "text", cache = True ) :
        uid = self.getRepoID( repopath, cache )
        if not self.hasBranch( repopath, branch, cache ) :
            assert False, "repo branch does not exist!"
        if self.hasFile( repopath, branch, filepath, cache ) :
            assert False, "file already exists!"
        
        if not ( encoding in [ "text", "base64" ] ) :
            assert False, "invalid encoding"

        result = git._git.createfile( uid, filepath, branch, encoding, data, commit_message )
        assert result == True, "internal error!"
    # end def
    
    def modFile( self, repo, branch, filepath, data, commit_message ) :
        # can also be used to create files with no care if it already exists or not :)
        
        # updatefile(self, project_id, file_path, branch_name, content, commit_message):
        pass
    # end def
    
    
# end class

# git = gilapt( sys.argv[1], sys.argv[2] )
# org = libOrg.libOrg( sys.argv[3] )
# table = org.findFirstTable()

# import pdb; pdb.set_trace()
