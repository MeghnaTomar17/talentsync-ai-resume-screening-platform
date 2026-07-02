import { Link } from 'react-router-dom';
import { Activity, FileCheck2, LineChart, UploadCloud } from 'lucide-react';
import Button from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { getAnalysis, getUpload } from '@/store/resumeStore';

export function DashboardPage() {
  const upload = getUpload();
  const analysis = getAnalysis();

  const metrics = [
    ['ATS Score', analysis?.ats_score ?? 0],
    ['Semantic Match', analysis?.semantic_score ?? 0],
    ['Skills Found', analysis?.skill_count ?? 0],
  ];

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">Dashboard</span>
          <h1>Resume intelligence workspace</h1>
          <p>Upload, analyze, coach, and map growth from one focused interface.</p>
        </div>
        <Link to="/app/upload">
          <Button>
            <UploadCloud size={18} /> Upload resume
          </Button>
        </Link>
      </section>

      <div className="metric-grid">
        {metrics.map(([label, value]) => (
          <Card key={label as string}>
            <CardHeader>
              <CardDescription>{label}</CardDescription>
              <CardTitle>{typeof value === 'number' ? Math.round(value) : value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </div>

      <div className="dashboard-grid">
        <Card>
          <CardHeader>
            <FileCheck2 size={22} />
            <CardTitle>Current resume</CardTitle>
            <CardDescription>
              {upload?.resume_text
                ? `${upload.resume_text.slice(0, 160)}...`
                : 'No resume uploaded yet.'}
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <Activity size={22} />
            <CardTitle>Recommended next step</CardTitle>
            <CardDescription>
              {analysis ? 'Review missing skills and generate an AI roadmap.' : 'Upload a PDF resume to begin.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to={analysis ? '/app/roadmap' : '/app/upload'}>
              <Button variant="outline">{analysis ? 'Open roadmap' : 'Upload resume'}</Button>
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <LineChart size={22} />
            <CardTitle>Best match</CardTitle>
            <CardDescription>
              {analysis?.best_match?.job_title || 'Run analysis to see top job matches.'}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
