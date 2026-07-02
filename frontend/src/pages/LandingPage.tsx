import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  FileSearch,
  Layers3,
  LineChart,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import Button from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

const features: Array<[string, string, LucideIcon]> = [
  ['Semantic job matching', 'Understands resume meaning beyond keyword overlap.', FileSearch],
  ['ATS scoring', 'Clear readiness metrics for recruiters and candidates.', ShieldCheck],
  ['AI coaching', 'Resume feedback, skill gaps, and next-step recommendations.', Bot],
  ['Career roadmap', 'Learning plans tied to target roles and missing skills.', LineChart],
];

const workflow = ['Upload resume', 'Extract skills', 'Match jobs', 'Score ATS fit', 'Coach growth'];

export function LandingPage() {
  return (
    <main>
      <section className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow">
            <Sparkles size={16} /> AI hiring intelligence
          </span>
          <h1>TalentSync AI</h1>
          <p>
            A modern resume screening platform that combines semantic search, ATS
            intelligence, and AI-guided career development.
          </p>
          <div className="hero-actions">
            <Link to="/app/upload">
              <Button size="lg">
                Analyze a resume <ArrowRight size={18} />
              </Button>
            </Link>
            <Link to="/auth/register">
              <Button size="lg" variant="outline">Create account</Button>
            </Link>
          </div>
        </div>
        <div className="hero-visual" aria-label="TalentSync product preview">
          <div className="score-orbit">
            <strong>92</strong>
            <span>ATS Fit</span>
          </div>
          <div className="preview-panel">
            <div className="preview-line wide" />
            <div className="preview-line" />
            <div className="preview-grid">
              <span>Python</span>
              <span>FastAPI</span>
              <span>Docker</span>
              <span>SQL</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section product-overview">
        <div>
          <span className="section-kicker">Product overview</span>
          <h2>One workspace for screening, explaining, and improving resumes.</h2>
        </div>
        <p>
          TalentSync turns a PDF resume into structured intelligence: parser quality,
          extracted skills, semantic job recommendations, ATS scoring, and coaching
          outputs ready for decision-making.
        </p>
      </section>

      <section className="section" id="workflow">
        <span className="section-kicker">AI workflow</span>
        <div className="workflow-grid">
          {workflow.map((step, index) => (
            <div className="workflow-step" key={step}>
              <span>{index + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section" id="features">
        <span className="section-kicker">Features</span>
        <div className="feature-grid">
          {features.map(([title, description, Icon]) => (
            <Card key={title as string}>
              <CardHeader>
                <Icon size={22} />
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section className="section stack-section" id="stack">
        <Card>
          <CardContent className="stack-content">
            <Layers3 size={28} />
            <div>
              <span className="section-kicker">Technology stack</span>
              <h2>FastAPI, React, FAISS, SentenceTransformers, Gemini, and PDF parsing.</h2>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="section why-section">
        <div>
          <span className="section-kicker">Why TalentSync</span>
          <h2>Explainable hiring signals for practical decisions.</h2>
        </div>
        <ul>
          {['Transparent scores', 'Skill gap clarity', 'Responsive SaaS UI', 'Candidate growth guidance'].map(
            (item) => (
              <li key={item}>
                <CheckCircle2 size={18} /> {item}
              </li>
            )
          )}
        </ul>
      </section>

      <footer className="marketing-footer">
        <span>TalentSync AI</span>
        <span>Resume screening and career intelligence</span>
      </footer>
    </main>
  );
}
