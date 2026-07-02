import { useQuery } from '@tanstack/react-query';
import { Map } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { getCareerRoadmap } from '@/services/resumeService';
import { getAnalysis } from '@/store/resumeStore';

function roadmapSteps(markdown: string) {
  return markdown
    .split(/\n(?=#|Week\s+\d)/)
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 8);
}

export function CareerRoadmapPage() {
  const analysis = getAnalysis();

  const query = useQuery({
    enabled: Boolean(analysis),
    queryKey: ['career-roadmap', analysis?.best_match?.job_title],
    queryFn: () =>
      getCareerRoadmap({
        resume_skills: analysis?.extracted_skills || [],
        missing_skills: analysis?.missing_skills || [],
        target_role: analysis?.best_match?.job_title || 'Career Growth',
      }),
  });

  if (!analysis) {
    return (
      <EmptyState
        icon={<Map size={30} />}
        title="No roadmap yet"
        description="Run resume analysis first to generate a personalized learning roadmap."
      />
    );
  }

  if (query.isLoading) {
    return (
      <div className="page-stack">
        <Skeleton className="skeleton-heading" />
        <Skeleton className="skeleton-card tall" />
      </div>
    );
  }

  if (query.isError) {
    return <EmptyState title="Roadmap unavailable" description="The roadmap endpoint returned an error." />;
  }

  const steps = roadmapSteps(query.data?.roadmap || '');

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">Career Roadmap</span>
          <h1>{query.data?.target_role || 'Career Growth'}</h1>
          <p>Learning progression, projects, certifications, and role milestones.</p>
        </div>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
          <CardDescription>Generated from missing skills and target role.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="timeline">
            {steps.map((step, index) => (
              <article className="timeline-item" key={`${step}-${index}`}>
                <span>{index + 1}</span>
                <p>{step.replace(/^#+\s*/, '')}</p>
              </article>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="analysis-grid">
        <Card>
          <CardHeader>
            <CardTitle>Certifications</CardTitle>
            <CardDescription>Prioritize credentials that prove role readiness.</CardDescription>
          </CardHeader>
          <CardContent className="recommendation-list">
            {(query.data?.recommendations || ['Role-focused portfolio certification']).map((item) => (
              <span key={item}>{item}</span>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recommended projects</CardTitle>
            <CardDescription>Build proof around missing skills.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="markdown-copy">
              Create a portfolio project that combines {analysis.missing_skills.slice(0, 3).join(', ') || 'target-role skills'} with measurable outcomes.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
