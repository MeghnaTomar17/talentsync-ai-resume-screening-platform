import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState } from '@/components/ui/Card';
import { getAnalysis, getUpload } from '@/store/resumeStore';
import type { ScoreBreakdown } from '@/types/api';

const colors = ['#2563eb', '#10b981', '#f59e0b'];

function breakdownRows(breakdown: ScoreBreakdown) {
  return [
    { label: 'Semantic similarity', component: breakdown.components.semantic_similarity },
    { label: 'Skill overlap', component: breakdown.components.skill_overlap },
    { label: 'Resume quality', component: breakdown.components.resume_quality },
  ];
}

export function ResumeAnalysisPage() {
  const analysis = getAnalysis();
  const upload = getUpload();

  if (!analysis) {
    return <EmptyState title="No analysis yet" description="Upload a resume first to see ATS and matching insights." />;
  }

  const scoreData = [
    { name: 'ATS', value: analysis.ats_score || 0 },
    { name: 'Semantic', value: analysis.semantic_score || 0 },
    { name: 'Quality', value: analysis.quality_report?.quality_score || 0 },
  ];

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">Analysis dashboard</span>
          <h1>{analysis.best_match?.job_title || 'Resume analysis'}</h1>
          <p>
            {analysis.job_source === 'provided'
              ? 'Scored against the job description you provided.'
              : 'Scored against the best matching job from the dataset.'}{' '}
            ATS scoring, parser quality, skills, and top semantic job matches.
          </p>
        </div>
      </section>

      <div className="metric-grid">
        {scoreData.map((metric) => (
          <Card key={metric.name}>
            <CardHeader>
              <CardDescription>{metric.name} Score</CardDescription>
              <CardTitle>{Math.round(metric.value)}%</CardTitle>
            </CardHeader>
          </Card>
        ))}
        <Card>
          <CardHeader>
            <CardDescription>Parser Used</CardDescription>
            <CardTitle>{upload?.extraction_metadata?.parser_used || 'Unknown'}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Extraction Confidence</CardDescription>
            <CardTitle>{upload?.extraction_metadata?.confidence ?? 0}%</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Resume Type</CardDescription>
            <CardTitle>{analysis.quality_report?.resume_type || 'Unknown'}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div className="analysis-grid">
        <Card>
          <CardHeader>
            <CardTitle>Score mix</CardTitle>
            <CardDescription>ATS, semantic, and quality signals.</CardDescription>
          </CardHeader>
          <CardContent className="chart-wrap">
            <ResponsiveContainer height={240} width="100%">
              <PieChart>
                <Pie data={scoreData} dataKey="value" innerRadius={62} outerRadius={92}>
                  {scoreData.map((entry, index) => (
                    <Cell fill={colors[index % colors.length]} key={entry.name} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Skill categories</CardTitle>
            <CardDescription>{analysis.skill_count} skills detected.</CardDescription>
          </CardHeader>
          <CardContent className="category-list">
            {Object.entries(analysis.categorized_skills).map(([category, skills]) => (
              <div key={category}>
                <strong>{category}</strong>
                <div className="badge-row">
                  {skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="analysis-grid">
        <Card>
          <CardHeader><CardTitle>Matched Skills</CardTitle></CardHeader>
          <CardContent className="badge-row">
            {analysis.matched_skills.map((skill) => <Badge className="badge-success" key={skill}>{skill}</Badge>)}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Missing Skills</CardTitle></CardHeader>
          <CardContent className="badge-row">
            {analysis.missing_skills.map((skill) => <Badge className="badge-warning" key={skill}>{skill}</Badge>)}
          </CardContent>
        </Card>
      </div>

      {(analysis.partial_matches?.length ?? 0) > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Partially covered skills</CardTitle>
            <CardDescription>Missing skills where the resume shows a closely related skill.</CardDescription>
          </CardHeader>
          <CardContent className="job-list">
            {analysis.partial_matches?.map((partial) => (
              <div className="partial-row" key={partial.skill}>
                <Badge className="badge-warning">{partial.skill}</Badge>
                <span>related: {partial.related_skills.join(', ')}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {analysis.score_breakdown && (
        <Card>
          <CardHeader>
            <CardTitle>Why this score?</CardTitle>
            <CardDescription>{analysis.score_breakdown.formula}</CardDescription>
          </CardHeader>
          <CardContent className="page-stack">
            {breakdownRows(analysis.score_breakdown).map((row) => (
              <div className="breakdown-row" key={row.label}>
                <div className="breakdown-label">
                  <strong>{row.label}</strong>
                  <span>
                    {row.component.contribution.toFixed(1)} / {row.component.max_contribution.toFixed(0)} pts
                  </span>
                </div>
                <Progress value={row.component.score} />
              </div>
            ))}
            {(analysis.explanation?.length ?? 0) > 0 && (
              <ul className="explanation-list">
                {analysis.explanation?.map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Top job matches</CardTitle>
          <CardDescription>Ranked by backend semantic retrieval.</CardDescription>
        </CardHeader>
        <CardContent className="job-list">
          {analysis.top_jobs.map((job, index) => (
            <div className="job-row" key={`${job.job_title}-${index}`}>
              <span>{index + 1}</span>
              <div>
                <strong>{job.job_title}</strong>
                <p>{job.job_description.slice(0, 160)}...</p>
              </div>
              <b>{Math.round(job.semantic_score)}%</b>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
