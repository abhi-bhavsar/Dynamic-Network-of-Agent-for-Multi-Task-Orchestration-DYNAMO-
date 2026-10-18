import React, { useState } from 'react';
import {
  FileText,
  Copy,
  Check,
  Download,
  Gauge,
  Printer,
  Sparkles,
} from 'lucide-react';

export default function ReportViewer({ report, confidence, query }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!report) return;
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!report) return;
    const blob = new Blob(
      [`# DYNAMO Synthesized Research Report\n\n**Query:** ${query}\n\n${report}`],
      { type: 'text/markdown' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dynamo_report_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const confPercent = Math.round((confidence || 0.88) * 100);

  // Render markdown with sections styled nicely
  const renderFormattedReport = (text) => {
    if (!text) {
      return (
        <div style={{ color: 'var(--text-dim)', fontStyle: 'italic', padding: '2rem 0', textAlign: 'center' }}>
          Enter a query above and execute DYNAMO to generate a synthesized research report.
        </div>
      );
    }

    const lines = text.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('## ')) {
        return (
          <h2 key={idx} style={{ marginTop: '1.25rem', marginBottom: '0.5rem', color: 'var(--cyan-bright)' }}>
            {line.replace('## ', '')}
          </h2>
        );
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        const content = line.substring(2);
        // Highlight bold text inside bullet
        const parts = content.split('**');
        return (
          <li key={idx} style={{ marginLeft: '1.25rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>
            {parts.map((p, i) => (i % 2 === 1 ? <strong key={i} style={{ color: 'var(--text-main)' }}>{p}</strong> : p))}
          </li>
        );
      }
      if (line.trim().startsWith('Overall Confidence:')) {
        return null; // rendered separately in the header gauge
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: '0.5rem' }} />;
      }
      return (
        <p key={idx} style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          {line}
        </p>
      );
    });
  };

  return (
    <div className="glass-panel report-panel">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <FileText size={22} color="#06b6d4" />
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Synthesized Research Report</h3>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Confidence-Weighted Integration from Active Specialist Agents
            </div>
          </div>
        </div>

        {/* Confidence Gauge & Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.4rem 0.85rem',
              background: 'rgba(6, 182, 212, 0.12)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '999px',
            }}
          >
            <Gauge size={16} color="var(--cyan-bright)" />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Overall Confidence:</span>
            <strong className="mono" style={{ color: 'var(--cyan-bright)', fontSize: '0.9rem' }}>
              {confPercent}%
            </strong>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <button
              className="btn-secondary"
              onClick={handleCopy}
              disabled={!report}
              title="Copy Report to Clipboard"
            >
              {copied ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy'}
            </button>

            <button
              className="btn-secondary"
              onClick={handleDownload}
              disabled={!report}
              title="Download as Markdown"
            >
              <Download size={14} />
              Export .md
            </button>

            <button
              className="btn-secondary"
              onClick={handlePrint}
              disabled={!report}
              title="Print / Save PDF"
            >
              <Printer size={14} />
            </button>
          </div>
        </div>
      </div>

      <div className="report-body">
        {renderFormattedReport(report)}
      </div>
    </div>
  );
}
