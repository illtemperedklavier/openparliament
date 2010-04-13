from collections import defaultdict

from django.template import Context, loader, RequestContext
from django.core.mail import send_mail

from parliament.alerts.models import PoliticianAlert
from parliament.core.templatetags.ours import english_list

def alerts_for_hansard(hansard):
    alerts = PoliticianAlert.objects.all()
    alert_set = set([alert.politician_id for alert in alerts])
    
    statements = defaultdict(list)
    topics = defaultdict(list)
    for statement in hansard.statement_set.all():
        pol_id = statement.politician_id
        if pol_id in alert_set:
            statements[pol_id].append(statement)
            topics[pol_id].append(statement.topic)
            
    for alert in alerts:
        if statements[pol_id]:
            pol_id = alert.politician_id
            pol = alert.politician
            c = Context({
                'alert': alert,
                'statements': statements[pol_id],
                'topics': topics[pol_id]
            })
            t = loader.get_template("alerts/politician.txt")
            msg = t.render(c)
            subj = u'%(politician)s spoke about %(topics)s in the House' % {
                'politician': pol.name,
                'topics': english_list(topics[pol_id])
            }
            subj = subj[:200]
            try:
                if 'michaelmulley' in alert.email:
                    send_mail(subject=subj,
                        message=msg,
                        from_email='alerts@openparliament.ca',
                        recipient_list=[alert.email])
                else:
                    print alert.email
                    print msg
            except Exception, e:
                # FIXME logging
                print "Error sending alert %s" % alert.id
                print e
        