#!/usr/bin/python2.6
"""Job directory creation daemon
"""
__author__  = "Michael Stella <mstella@charlex.com>"
__version__ = '$Id: jobDirectoryCreator.py 9559 2016-10-31 04:47:50Z zwillie $'

import datetime, ldap, os, shutil, smtplib, sys, time
from email.mime.text        import MIMEText

import chrlx
from chrlx                  import CHRLXCFG, PATHS, utils
from chrlx.model.meta       import Session
from chrlx.model.jobs       import Job, Shot

def run():
    ## create new job directories
    for job in Session.query(Job).filter_by(status='N'):
        if os.path.isdir(job.path):
            print("%s already exists, marking active" % job.dir_name)
            job.status = 'A'
            Session.commit()
        else:
            createJobDirectories(job)
            sendJobEmail(job)


    ## create new spot directories - must do this by job,
    ## but only for active jobs
    for job in Session.query(Job).filter_by(status='A'):
        newSpots = []
        for spot in job.spots:
            if spot.status != 'N':
                continue
            if os.path.isdir(spot.path):
                print("%s/%s already exists, marking active" % (spot.job.dir_name, spot.dir_name))
                spot.status = 'A'
                Session.commit()

            else:
                createSpotDirectories(spot)
                newSpots.append(spot)

        if newSpots:
            sendJobEmail(job, newSpots)

def createJobDirectories(job):
    print("Creating job directory for " + job.dir_name)

    try:
        os.mkdir(job.path)
    except OSError, e:
        print("Error creating directory %s: %s" % (job.path, e.strerror))
        return

    # run through all the spots
    spots = []
    for spot in job.spots:
        if spot.status == 'N':
            createSpotDirectories(spot)
            spots.append(spot)

    # calendar directory
    caldir = os.path.join(job.path, 'calendar')
    os.mkdir(caldir)
    os.chmod(caldir, 0777)

    # make sure job/spot paths are read-only
    utils.chown(job.path, 0, 600)
    os.chmod(job.path, 0555)

    # mark the job done, and save it all
    job.status = 'A'
    job.addComment(uid='rush3d', subject='Job directory created')
    Session.commit()

def createSpotDirectories(spot):
    if not os.path.exists(spot.path):
        print("Creating spot directory for %s/%s" % (spot.job.dir_name, spot.dir_name))
        os.mkdir(spot.path)
        utils.chown(spot.path, 0, 600)
        os.chmod(spot.path, 0555)

    # create spot subdirs
    spotsConfig = 'directory-spots.config'
    if spot.schema>1:
        spotsConfig='directory-spots-v2.config'

    with open(os.path.join(PATHS['CHRLX_3D_CFG'], spotsConfig)) as f:
        for p in f:
            p = p.strip()
            if not p:
                continue
            if p.startswith('#'):
                continue

            thispath = os.path.join(spot.path, p.lstrip('/'))
            if not os.path.exists(thispath):
                os.mkdir(thispath)
                os.chmod(thispath, 0777)
                utils.chown(thispath, 0, 600)

    if not os.path.exists(os.path.join(spot.projectPath, 'workspace.mel')):
        shutil.copy(os.path.join(PATHS['CHRLX_3D_CFG'], 'workspace.mel'), spot.projectPath)
        os.chmod(os.path.join(spot.projectPath, 'workspace.mel'), 0644)

    # mark spot done
    spot.status = 'A'
    Session.commit()

def createShot(jobname, spotname, shotname, fps=None, startframe=None, endframe=None, camera=None, resolution=None, description=None, uid=None):
    """create new shot by calling the existing perl script"""
    if not uid:
        uid=utils.getCurrentUser()
    shotnum=int(shotname[-3:])
    stage=shotname[:-3]
    spotPath=utils.PathManager(os.path.join(PATHS['CHRLX_JOBS'], jobname, spotname))
    shot = Session.query(Shot).filter_by(spotid=spotPath.spot.id, shot=shotnum, stage=stage).first()
    if not shot:
        shot=Shot(spotid=str(spotPath.spot.id),
             uid=uid,
             shot=shotnum,
             stage=stage,
             start_frame=startframe,
             end_frame=endframe,
             fps=fps,
             resolution=resolution,
             camera=camera,
             description=description)
        Session.add(shot)
        Session.commit()
        print "Adding Shot", spotPath.spot, shotname
    else:
        print "Shot Exists", spotPath.spot, shotname
    shotsConfig = 'directory-shots.config'
    if spotPath.spot.schema>1:
        shotsConfig='directory-shots-v2.config'
    with open(os.path.join(PATHS['CHRLX_3D_CFG'], shotsConfig)) as f:
        for p in f:
            p = p.strip()
            if not p:
                continue
            if p.startswith('#'):
                continue
            p= p.lstrip('/')
            thispath = os.path.join(spotPath, p%(stage, shotnum))
            if not os.path.exists(thispath):
                os.mkdir(thispath)
                os.chmod(thispath, 0777)
                utils.chown(thispath, 0, 600)

    return utils.PathManager(shot.path)


def sendJobEmail(job, newspots=None):
    """Sends the new job email"""

    from pwd import getpwnam

    try:
        username = getpwnam(job.uid)[4]
    except:
        username = job.uid
    if (newspots):
        sender = "Intranet <rush3d@charlex.com>"
    else:
        sender = "%s <%s@charlex.com>" % (username, job.uid)

    # send to me if we're in test mode
    if os.getenv('CHRLX_DB_TEST'):
        target = 'psultan@charlex.com'
    else:
        target = 'apache_list@charlex.com'

    spottmpl = ''
    with open(os.path.join(PATHS['CHRLX_3D_CFG'], 'email.spotCreation.html')) as f:
        spottmpl = f.read()

    spotbody = ''
    # if passed spots, these are the only ones to display, they're new
    if newspots:
        subject = "Added new spot for: [%s]" % job.dir_name
        for s in newspots:
            spotbody += spottmpl.format(spot = s,
                                        letter=s.letter,
                                        link = s.link)


    # otherwise use the job's spots
    else:
        subject = "New Job Created: [%s]" % job.dir_name
        for s in job.spots:
            spotbody += spottmpl.format(spot = s,
                                        letter=s.letter,
                                        link = s.link)


    # now read the job template and format the job
    jobtmpl = ''
    with open(os.path.join(PATHS['CHRLX_3D_CFG'], 'email.jobCreation.html')) as f:
        jobtmpl = f.read()

    # ldap lookup various people
    producer          = getPerson(job.producer)
    senior_producer   = getPerson(job.senior_producer)
    creative_director = getPerson(job.creative_director)

    body = jobtmpl.format(
            job             = job,
            spots           = spotbody,
            link            = job.link,
            datenow         = datetime.datetime.now().strftime('%F at %H:%M'),
            version         = __version__.split()[2],
            awarded_text    = 'yes: ' + job.awarded_bid_number if job.awarded == 'Y' else 'no',
            username        = username,
            producer          = producer if producer else job.producer,
            senior_producer   = senior_producer if senior_producer else job.senior_producer,
            creative_director = creative_director if creative_director else job.creative_director,
            )

    # now create the real MIME message
    msg = MIMEText(body, 'html')
    msg['From'] = sender
    msg['To'] = target
    msg['Subject'] = subject

    # aaaaand... send it!
    s = smtplib.SMTP('mail.charlex.com')
    s.sendmail(sender, [target], msg.as_string())
    s.quit()
def getPerson(uid):
    """Look up a person and return the cn, mail, formatted for html display"""
    chrlxLdap = ldap.initialize('ldap://ldap.charlex.com/')
    chrlxLdap.bind_s('','')

    res = chrlxLdap.search_s(
        'ou=People,dc=charlex,dc=com', ldap.SCOPE_SUBTREE,
        '(uid=%s)' % uid,
        ['cn', 'mail', 'sn', 'givenName'])

    if not res:
        return None

    return "%s &lt;%s&gt;" % (res[0][1]['cn'][0], res[0][1]['mail'][0])

def main(argv):
    if sys.platform != "linux2":
        print("This program only works on linux.")
        sys.exit(1)
    if os.getuid() != 0:
        print("This program may only be run as root.")
        sys.exit(1)
    else:
        run()

if __name__ == '__main__':
    main(sys.argv)

