from django.contrib import admin
from .models import (
    Company,
    ResumeVersion,
    CoverLetterVersion,
    JobPosting,
    Application,
    Interview,
    OutcomeReview,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'website')
    search_fields = ('name', 'industry', 'notes')


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_role', 'created_at')
    list_filter = ('target_role', 'created_at')
    search_fields = ('name', 'skill_summary', 'experience_summary', 'notes')


@admin.register(CoverLetterVersion)
class CoverLetterVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_role', 'created_at')
    search_fields = ('name', 'target_role', 'key_message', 'notes')


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    fields = ('round_number', 'interview_date', 'interview_type', 'interviewers', 'result')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'role_type', 'location', 'work_type', 'date_saved', 'platform')
    list_filter = ('role_type', 'work_type', 'platform', 'date_saved')
    search_fields = ('title', 'company__name', 'location', 'jd_text', 'jd_skill_summary', 'jd_experience_summary')
    date_hierarchy = 'date_saved'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'status', 'date_applied', 'days_since_applied_display', 'has_reply', 'reply_date', 'interview_count_display', 'next_action_date')
    list_filter = ('status', 'has_reply', 'date_applied', 'job__role_type')
    search_fields = ('job__title', 'job__company__name', 'notes', 'match_notes', 'current_stage')
    autocomplete_fields = ('job', 'resume', 'cover_letter')
    inlines = [InterviewInline]
    date_hierarchy = 'date_applied'

    @admin.display(description='Days since applied')
    def days_since_applied_display(self, obj):
        return obj.days_since_applied

    @admin.display(description='Interviews')
    def interview_count_display(self, obj):
        return obj.interview_count


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'round_number', 'interview_date', 'interview_type', 'result')
    list_filter = ('result', 'interview_type', 'interview_date')
    search_fields = ('application__job__title', 'application__job__company__name', 'questions_asked', 'performance_notes')


@admin.register(OutcomeReview)
class OutcomeReviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'failed_at_stage', 'created_at')
    list_filter = ('failed_at_stage', 'created_at')
    search_fields = ('application__job__title', 'application__job__company__name', 'reason_given', 'my_diagnosis', 'action_for_next_application')
