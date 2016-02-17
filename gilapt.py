import sys

sys.path.append( "./lib/requests" )
sys.path.append( "./lib/gitlab" )
sys.path.append( "./lib/org/py" )

import gitlab
import libOrg

if len( sys.argv ) != 2 :
    sys.stderr.write( "%s: error: provide a GitLab access token!\n" % sys.argv[0] )
    sys.exit(-1)

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
