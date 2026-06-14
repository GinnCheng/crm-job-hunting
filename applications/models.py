from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class ResumeVersion(TimeStampedModel):
    TARGET_ROLE_CHOICES = [
        ('data_engineering', 'Data Engineering'),
        ('data_science', 'Data Science'),
        ('quant_modelling', 'Quant / Modelling'),
        ('energy_analyst', 'Energy Analyst'),
        ('environmental_consulting', 'Environmental Consulting'),
        ('digital_consulting', 'Digital Consulting'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    target_role = models.CharField(max_length=80, choices=TARGET_ROLE_CHOICES, default='data_engineering')
    file = models.FileField(upload_to='resumes/', blank=True)
    external_file_path = models.CharField(max_length=800, blank=True, help_text='Optional path to a file in RESUME_FOLDER.')
    skill_summary = models.TextField(blank=True)
    experience_summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CoverLetterVersion(TimeStampedModel):
    name = models.CharField(max_length=200)
    target_role = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to='cover_letters/', blank=True)
    external_file_path = models.CharField(max_length=800, blank=True, help_text='Optional path to a file in COVER_LETTER_FOLDER.')
    key_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class JobPosting(TimeStampedModel):
    WORK_TYPE_CHOICES = [
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
        ('unknown', 'Unknown'),
    ]
    ROLE_TYPE_CHOICES = [
        ('data_engineering', 'Data Engineering'),
        ('data_analytics', 'Data Analytics'),
        ('data_science', 'Data Science'),
        ('quant_modelling', 'Quant / Modelling'),
        ('energy', 'Energy'),
        ('environmental', 'Environmental'),
        ('digital', 'Digital'),
        ('other', 'Other'),
    ]
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='jobs')
    title = models.CharField(max_length=250)
    role_type = models.CharField(max_length=80, choices=ROLE_TYPE_CHOICES, default='data_engineering')
    location = models.CharField(max_length=160, blank=True)
    work_type = models.CharField(max_length=40, choices=WORK_TYPE_CHOICES, default='unknown')
    salary_range = models.CharField(max_length=120, blank=True)
    job_url = models.URLField(blank=True)
    platform = models.CharField(max_length=100, blank=True, help_text='LinkedIn, Seek, Indeed, company website, recruiter, etc.')
    date_posted = models.DateField(null=True, blank=True)
    date_saved = models.DateField(default=timezone.localdate)
    jd_text = models.TextField(blank=True)
    jd_skill_summary = models.TextField(blank=True)
    jd_experience_summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_saved', 'company__name', 'title']

    def __str__(self):
        return f'{self.title} - {self.company.name}'


class Application(TimeStampedModel):
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('ghosted', 'Ghosted'),
    ]
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(ResumeVersion, on_delete=models.SET_NULL, null=True, blank=True)
    cover_letter = models.ForeignKey(CoverLetterVersion, on_delete=models.SET_NULL, null=True, blank=True)
    date_applied = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='saved')
    has_reply = models.BooleanField(default=False)
    reply_date = models.DateField(null=True, blank=True)
    current_stage = models.CharField(max_length=160, blank=True)
    next_action = models.CharField(max_length=250, blank=True)
    next_action_date = models.DateField(null=True, blank=True)
    cv_skill_summary = models.TextField(blank=True)
    cv_experience_summary = models.TextField(blank=True)
    match_notes = models.TextField(blank=True, help_text='JD vs CV fit, gaps, tailored story.')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_applied', '-created_at']

    def __str__(self):
        return f'{self.job} [{self.get_status_display()}]'

    @property
    def days_since_applied(self):
        if not self.date_applied:
            return None
        return (timezone.localdate() - self.date_applied).days

    @property
    def days_to_reply(self):
        if self.date_applied and self.reply_date:
            return (self.reply_date - self.date_applied).days
        return None

    @property
    def interview_count(self):
        return self.interviews.count()


class Interview(TimeStampedModel):
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    round_number = models.PositiveIntegerField(default=1)
    interview_date = models.DateField(null=True, blank=True)
    interview_type = models.CharField(max_length=120, blank=True, help_text='HR screen, technical, hiring manager, final, etc.')
    interviewers = models.CharField(max_length=250, blank=True)
    questions_asked = models.TextField(blank=True)
    performance_notes = models.TextField(blank=True)
    result = models.CharField(max_length=40, choices=RESULT_CHOICES, default='pending')

    class Meta:
        ordering = ['application', 'round_number']

    def __str__(self):
        return f'{self.application.job.title} - Round {self.round_number}'


class OutcomeReview(TimeStampedModel):
    FAILED_STAGE_CHOICES = [
        ('screening', 'Screening'),
        ('first_interview', 'First Interview'),
        ('technical', 'Technical Interview'),
        ('hiring_manager', 'Hiring Manager'),
        ('final', 'Final Round'),
        ('offer_negotiation', 'Offer Negotiation'),
        ('unknown', 'Unknown'),
    ]
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='outcome_review')
    failed_at_stage = models.CharField(max_length=80, choices=FAILED_STAGE_CHOICES, default='unknown')
    reason_given = models.TextField(blank=True)
    my_diagnosis = models.TextField(blank=True)
    skill_gap = models.TextField(blank=True)
    communication_gap = models.TextField(blank=True)
    cv_issue = models.TextField(blank=True)
    cover_letter_issue = models.TextField(blank=True)
    salary_or_location_issue = models.TextField(blank=True)
    action_for_next_application = models.TextField(blank=True)

    def __str__(self):
        return f'Outcome review - {self.application.job}'
