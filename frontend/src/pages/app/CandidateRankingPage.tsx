import { useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { UploadCloud, Users } from 'lucide-react';
import Button from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Progress } from '@/components/ui/Progress';
import { useToast } from '@/hooks/useToast';
import { rankCandidates, uploadResume } from '@/services/resumeService';

const MAX_CANDIDATES = 50;

export function CandidateRankingPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const { showToast } = useToast();

  const mutation = useMutation({
    mutationFn: async () => {
      setProgress(5);
      const candidates = [];
      // Parse each PDF with the existing upload endpoint, then rank them together
      for (const [index, file] of files.entries()) {
        const uploaded = await uploadResume(file);
        candidates.push({
          candidate_id: file.name,
          resume_text: uploaded.resume_text || uploaded.cleaned_text || '',
        });
        setProgress(Math.round(((index + 1) / files.length) * 80));
      }
      const result = await rankCandidates({
        job_description: jobDescription,
        job_title: jobTitle.trim() || undefined,
        candidates,
      });
      setProgress(100);
      return result;
    },
    onSuccess: () => showToast('Candidates ranked.'),
    onError: (failure) => {
      setProgress(0);
      showToast(failure instanceof Error ? failure.message : 'Ranking failed', 'error');
    },
  });

  function selectFiles(list?: FileList | null) {
    setError('');
    if (!list) return;
    const selected = Array.from(list);
    const pdfs = selected.filter((file) => file.type === 'application/pdf');
    if (pdfs.length !== selected.length) {
      setError('Only PDF files are supported; other files were ignored.');
    }
    if (pdfs.length > MAX_CANDIDATES) {
      setError(`You can rank up to ${MAX_CANDIDATES} resumes at once.`);
    }
    setFiles(pdfs.slice(0, MAX_CANDIDATES));
  }

  const canRank = files.length > 0 && jobDescription.trim().length > 0 && !mutation.isPending;
  const data = mutation.data;

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">Candidate ranking</span>
          <h1>Rank resumes for one job</h1>
          <p>Every resume is scored with the same ATS pipeline and sorted by score. Scores support, not replace, recruiter judgement.</p>
        </div>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Job description</CardTitle>
          <CardDescription>All candidates are compared against this description.</CardDescription>
        </CardHeader>
        <CardContent className="form-stack">
          <label className="field-label">
            Job title
            <Input onChange={(event) => setJobTitle(event.target.value)} placeholder="e.g. Backend Engineer" value={jobTitle} />
          </label>
          <label className="field-label">
            Job description
            <textarea
              className="textarea"
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the job description here"
              rows={8}
              value={jobDescription}
            />
          </label>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <div
            className="upload-dropzone"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              selectFiles(event.dataTransfer.files);
            }}
          >
            <UploadCloud size={36} />
            <h2>Drop candidate PDFs here</h2>
            <p>{files.length ? `${files.length} resume(s) selected` : `Up to ${MAX_CANDIDATES} PDF resumes.`}</p>
            <input
              accept="application/pdf"
              hidden
              multiple
              onChange={(event) => selectFiles(event.target.files)}
              ref={inputRef}
              type="file"
            />
            <Button onClick={() => inputRef.current?.click()} type="button" variant="outline">
              Choose files
            </Button>
          </div>
          {error && <p className="field-error">{error}</p>}
          <Progress value={progress} />
          <div className="form-actions">
            <Button disabled={!canRank} onClick={() => mutation.mutate()}>
              {mutation.isPending ? 'Ranking...' : 'Rank candidates'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {!data && !mutation.isPending && (
        <EmptyState icon={<Users size={30} />} title="No ranking yet" description="Add a job description and resumes to rank candidates." />
      )}

      {data && (
        <>
          <div className="metric-grid">
            <Card>
              <CardHeader>
                <CardDescription>Candidates</CardDescription>
                <CardTitle>{data.summary.total_candidates}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Average ATS</CardDescription>
                <CardTitle>{Math.round(data.summary.average_ats_score ?? 0)}%</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Highest ATS</CardDescription>
                <CardTitle>{Math.round(data.summary.highest_ats_score ?? 0)}%</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Job skills detected</CardDescription>
                <CardTitle>{data.job_skills.length}</CardTitle>
              </CardHeader>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Most common skill gaps</CardTitle>
              <CardDescription>Job skills missing from the most candidates.</CardDescription>
            </CardHeader>
            <CardContent className="badge-row">
              {(data.summary.most_common_missing_skills ?? []).map((gap) => (
                <Badge className="badge-warning" key={gap.skill}>
                  {gap.skill} · {gap.count}
                </Badge>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ranked candidates</CardTitle>
              <CardDescription>{data.job_title}</CardDescription>
            </CardHeader>
            <CardContent className="job-list">
              {data.candidates.map((candidate) => (
                <details className="ranking-row" key={candidate.candidate_id}>
                  <summary>
                    <span>{candidate.rank}</span>
                    <div>
                      <strong>{candidate.candidate_id}</strong>
                      <p>
                        Semantic {Math.round(candidate.semantic_score)}% · Skills {Math.round(candidate.skill_overlap_score)}% ·
                        Quality {Math.round(candidate.quality_score)}%
                      </p>
                    </div>
                    <b>{Math.round(candidate.ats_score)}%</b>
                  </summary>
                  <div className="ranking-details">
                    <div className="badge-row">
                      {candidate.matched_skills.map((skill) => <Badge className="badge-success" key={skill}>{skill}</Badge>)}
                      {candidate.missing_skills.map((skill) => <Badge className="badge-warning" key={skill}>{skill}</Badge>)}
                    </div>
                    <ul className="explanation-list">
                      {candidate.explanation.map((reason) => <li key={reason}>{reason}</li>)}
                    </ul>
                  </div>
                </details>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
