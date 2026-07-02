import { useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { FileText, UploadCloud } from 'lucide-react';
import Button from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { useToast } from '@/hooks/useToast';
import { analyzeResume, uploadResume } from '@/services/resumeService';
import { saveAnalysis, saveUpload } from '@/store/resumeStore';

export function ResumeUploadPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const { showToast } = useToast();

  const mutation = useMutation({
    mutationFn: async (selectedFile: File) => {
      setProgress(25);
      const uploaded = await uploadResume(selectedFile);
      saveUpload(uploaded);
      setProgress(70);
      const analysis = await analyzeResume(uploaded.cleaned_text || uploaded.resume_text || '');
      saveAnalysis(analysis);
      setProgress(100);
      return { uploaded, analysis };
    },
    onSuccess: () => showToast('Resume uploaded and analyzed.'),
    onError: (failure) => {
      setProgress(0);
      showToast(failure instanceof Error ? failure.message : 'Upload failed', 'error');
    },
  });

  function selectFile(nextFile?: File) {
    setError('');
    if (!nextFile) return;
    if (nextFile.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      setFile(null);
      return;
    }
    setFile(nextFile);
  }

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <span className="section-kicker">Resume upload</span>
          <h1>Upload a candidate resume</h1>
          <p>Drag in a PDF or use the file picker to run parsing and analysis.</p>
        </div>
      </section>

      <Card>
        <CardContent>
          <div
            className="upload-dropzone"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              selectFile(event.dataTransfer.files[0]);
            }}
          >
            <UploadCloud size={36} />
            <h2>Drop PDF resume here</h2>
            <p>PDF validation runs before upload.</p>
            <input
              accept="application/pdf"
              hidden
              onChange={(event) => selectFile(event.target.files?.[0])}
              ref={inputRef}
              type="file"
            />
            <Button onClick={() => inputRef.current?.click()} type="button" variant="outline">
              Choose file
            </Button>
          </div>
          {error && <p className="field-error">{error}</p>}
        </CardContent>
      </Card>

      {file && (
        <Card>
          <CardHeader>
            <FileText size={22} />
            <CardTitle>{file.name}</CardTitle>
            <CardDescription>{Math.round(file.size / 1024)} KB PDF ready for analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={progress} />
            <div className="form-actions">
              <Button disabled={mutation.isPending} onClick={() => mutation.mutate(file)}>
                {mutation.isPending ? 'Processing...' : 'Upload and analyze'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {mutation.isSuccess && (
        <Card>
          <CardHeader>
            <CardTitle>Upload complete</CardTitle>
            <CardDescription>
              Parser: {mutation.data.uploaded.extraction_metadata?.parser_used || 'Unknown'} ·
              Confidence: {mutation.data.uploaded.extraction_metadata?.confidence ?? 0}%
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}
