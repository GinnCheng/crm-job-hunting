from collections import Counter
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from .models import Application, Interview, ResumeVersion, JobPosting


def dashboard(request):
    today = timezone.localdate()
    applications = Application.objects.select_related('job', 'job__company', 'resume', 'cover_letter').all()

    total = applications.count()
    applied = applications.exclude(status='saved').count()
    replies = applications.filter(has_reply=True).count()
    interviews = applications.filter(interviews__isnull=False).distinct().count()
    offers = applications.filter(status='offer').count()
    rejected = applications.filter(status='rejected').count()
    ghosted = applications.filter(status='ghosted').count()

    reply_rate = round(replies / applied * 100, 1) if applied else 0
    interview_rate = round(interviews / applied * 100, 1) if applied else 0
    offer_rate = round(offers / applied * 100, 1) if applied else 0


    # SQLite date averaging is awkward; calculate in Python instead.
    reply_days = [a.days_to_reply for a in applications if a.days_to_reply is not None]
    avg_reply_days = round(sum(reply_days) / len(reply_days), 1) if reply_days else None

    status_counts = applications.values('status').annotate(count=Count('id')).order_by('status')
    role_counts = JobPosting.objects.values('role_type').annotate(count=Count('id')).order_by('role_type')

    upcoming_actions = applications.exclude(next_action_date__isnull=True).order_by('next_action_date')[:10]
    recent_applications = applications.order_by('-date_applied', '-created_at')[:15]
    stale_applications = [a for a in applications if a.status == 'applied' and a.days_since_applied is not None and a.days_since_applied >= 14 and not a.has_reply]

    resume_effectiveness = (
        ResumeVersion.objects
        .annotate(total_apps=Count('application'), interviews=Count('application__interviews', distinct=True))
        .order_by('-total_apps')[:10]
    )

    context = {
        'today': today,
        'total': total,
        'applied': applied,
        'replies': replies,
        'interviews': interviews,
        'offers': offers,
        'rejected': rejected,
        'ghosted': ghosted,
        'reply_rate': reply_rate,
        'interview_rate': interview_rate,
        'offer_rate': offer_rate,
        'avg_reply_days': avg_reply_days,
        'status_counts': status_counts,
        'role_counts': role_counts,
        'upcoming_actions': upcoming_actions,
        'recent_applications': recent_applications,
        'stale_applications': stale_applications[:10],
        'resume_effectiveness': resume_effectiveness,
    }
    return render(request, 'applications/dashboard.html', context)
