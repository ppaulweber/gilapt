import sys

sys.path.append( "./lib/requests" )
sys.path.append( "./lib/gitlab" )
sys.path.append( "./lib/org/py" )

import gitlab
import libOrg

if len( sys.argv ) != 2 :
    sys.stderr.write( "%s: error: provide a GitLab access token!\n" % sys.argv[0] )
    sys.exit(-1)

class gilapt(object):
    """GitLab Python Tool"""
    
    def __init__( self, host, token = "" ) :    
        self._git = gitlab.Gitlab( "https://%s" % host, token )

        self._users   = None
        self._id2user = {}
        
        self._groups = None
        self._id2group = {}
        
        self._repos  = None
        self._id2repo = {}
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
        
        if len( users ) == 0 :
            return {}
        elif len( users ) > 1 :
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
            return None
        
        if len( result ) == 0 :
            return False
        elif len( result ) != 0 :
            return True
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

    
# end class


git = gitlab.Gitlab( "https://gitlab.swa.univie.ac.at", token=sys.argv[1] )
org = libOrg.libOrg( "test.org" )
        
# generic function can be moved to 'liborg' repository!
def findTable( org ) :
    if isinstance( org, libOrg.libOrg ) :
        return findTable( org._content )
    elif isinstance( org, libOrg.OrgModeContent ) :
        for c in org._content :
            if isinstance( c, libOrg.Table ) :
                return c
    else :
        assert "invalid 'org' object to analyze"
    return None
# end def

# generic function can be moved to 'liborg' repository!
def iterateTable( org, row_action = lambda y, row : True, cell_action = lambda x, y, cell : None ) :
    def print_row( y, row ) :
        print y, row
        return True
    # end def
    def print_cell( x, y, row ) :
        print x, y, row        
    # end def
    if row_action is None :
        row_action = print_row
    if cell_action is None :
        cell_action = print_cell
    
    assert isinstance( org, libOrg.Table )    
    y = 0
    for row in org._content :
        assert isinstance( row, libOrg.TableRow )
        # print row
        result = row_action( y, row )
        if result == True or result is None :
            x = 0
            for cell in row._content :
                assert isinstance( cell, libOrg.TableCell )
                # print cell
                cell_action( x, y, cell )
                x = x + 1
        y = y + 1
# end def

table = findTable( org )

if table is None :
    sys.exit(-1)

def process_row( y, row ) :
    if row.columns[0] is None :
        return False

    print row, row.columns[0], row.columns[0] is None
    # return True
# end def

iterateTable( table, process_row )


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
