import { useQuery } from '@tanstack/react-query';
import { BrainCircuit } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { getResumeFeedback } from '@/services/resumeService';
import { getAnalysis, getUpload } from '@/store/resumeStore';

function sectionFromFeedback(markdown: string, heading: string) {
  const parts = markdown.split(/^# /gm);
  const match = parts.find((part) => part.toLowerCase().startsWith(heading.toLowerCase()));
  return match?.replace(new RegExp(`^${heading}`, 'i'), '').trim() || 'No details generated yet.';
}

export function ResumeCoachPage() {
  const upload = getUpload();
  const analysis = getAnalysis();

  const query = useQuery({
    enabled: Boolean(upload?.cleaned_text && analysis),
    queryKey: ['resume-feedback', analysis?.best_match?.job_title],
    queryFn: () =>
      getResumeFeedback({
        resume_text: upload?.cleaned_text || '',
        resume_skills: analysis?.extracted_skills || [],
        job_title: analysis?.best_match?.job_title,
        job_description: analysis?.best_match?.job_description,
      }),
  });

  if (!upload || !analysis) {
    return (
      <EmptyState
        icon={<BrainCircuit size={30} />}
        title="No coaching data"
        description="Upload and analyze a resume before generating AI coach insights."
      />
    );
  }

  if (query.isLoading) {
    return (
      <div className="page-stack">
        <Skeleton className="skeleton-heading" />
        <div className="analysis-grid">
          <Skeleton className="skeleton-card" />
          <Skeleton className="skeleton-card" />
        </div>
      </div>
    );
  }

  if (query.isError) {
    return <EmptyState title="Coach unavailable" description="The resume feedback endpoint returned an error." />;
  }

  const feedback = query.data?.feedback || '';
  const cards = [
    ['Strengths', sectionFromFeedback(feedback, 'Strengths')],
    ['Weaknesses', sectionFromFeedback(feedback, 'Weaknesses')],
    ['ATS recommendations', sectionFromFeedback(feedback, 'ATS Improvement Suggestions')],
    ['Career recommendations', sectionFromFeedback(feedback, 'Learning Recommendations')],
  ];

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">AI Resume Coach</span>
          <h1>Personalized resume guidance</h1>
          <p>Generated from resume content, detected skills, and target job fit.</p>
        </div>
      </section>

      <div className="analysis-grid">
        {cards.map(([title, body]) => (
          <Card key={title}>
            <CardHeader>
              <CardTitle>{title}</CardTitle>
              <CardDescription>{title === 'ATS recommendations' ? 'Improve parseability and keyword alignment.' : 'AI-generated insight.'}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="markdown-copy">{body}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Missing skills</CardTitle>
          <CardDescription>Skills the best-matched role expects.</CardDescription>
        </CardHeader>
        <CardContent className="recommendation-list">
          {analysis.missing_skills.map((skill) => <span key={skill}>{skill}</span>)}
        </CardContent>
      </Card>
    </div>
  );
}
