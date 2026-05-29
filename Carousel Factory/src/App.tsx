import React, { useState } from 'react';
import { Play, Loader2, Image as ImageIcon, AlertCircle, Download, FileJson, Edit2, Check, X, RefreshCw } from 'lucide-react';

export default function App() {
  const [url, setUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [slides, setSlides] = useState<string[]>([]);
  const [contentPlan, setContentPlan] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [logs, setLogs] = useState('');
  
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editBody, setEditBody] = useState('');

  const generateCarousel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url || !topic) return;
    
    setLoading(true);
    setError('');
    setSlides([]);
    setContentPlan([]);
    setLogs('');

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, topic })
      });
      
      const data = await res.json();
      
      if (data.slides && data.slides.length > 0) {
        setSlides(data.slides);
      }
      if (data.contentPlan) {
        setContentPlan(data.contentPlan);
      }
      
      if (!data.success) {
        setError('The pipeline encountered an error. Check the logs below.');
      }
      setLogs(data.logs || 'No logs available from processing.');
    } catch (err: any) {
      setError(err.message || 'Failed to communicate with the server.');
    } finally {
      setLoading(false);
    }
  };

  const saveSlideEdit = async () => {
    if (editingIndex === null) return;
    
    const newPlan = [...contentPlan];
    newPlan[editingIndex] = {
        ...newPlan[editingIndex],
        title: editTitle,
        body: editBody
    };
    
    setContentPlan(newPlan);
    setEditingIndex(null);
    
    // Trigger Rerender
    setLoading(true);
    try {
      const res = await fetch('/api/rerender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contentPlan: newPlan })
      });
      const data = await res.json();
      if (data.slides && data.slides.length > 0) {
        setSlides(data.slides);
      }
      if (!data.success) {
        setError('The rerender pipeline encountered an error. Check the logs below.');
      }
      setLogs(logs + '\n' + (data.logs || ''));
    } catch (err: any) {
      setError(err.message || 'Failed to rerender.');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (i: number) => {
      setEditingIndex(i);
      setEditTitle(contentPlan[i]?.title || '');
      setEditBody(contentPlan[i]?.body || '');
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-blue-500/30">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <ImageIcon size={18} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-xl tracking-tight text-white">Carousel Factory</h1>
              <p className="text-xs text-zinc-400 font-medium">Autonomous Design Engine</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          
          {/* Controls Column */}
          <div className="lg:col-span-4 space-y-8">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-2xl">
              <h2 className="text-lg font-semibold mb-6 flex items-center text-white">
                <span className="bg-zinc-800 p-1.5 rounded-md mr-3">
                  <FileJson size={16} className="text-zinc-300" />
                </span>
                Campaign Configuration
              </h2>
              <form onSubmit={generateCarousel} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Brand URL</label>
                  <input 
                    type="url" 
                    required
                    placeholder="https://example.com"
                    value={url}
                    onChange={e => setUrl(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Product or Topic Name</label>
                  <input 
                    type="text" 
                    required
                    placeholder="Why AI is the future of design..."
                    value={topic}
                    onChange={e => setTopic(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                  />
                </div>
                
                <button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg flex items-center justify-center space-x-2 transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Processing Pipeline...</span>
                    </>
                  ) : (
                    <>
                      <Play size={18} fill="currentColor" />
                      <span>Generate Carousel</span>
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Status/Logs */}
            {(logs || error) && (
              <div className="bg-black/50 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-zinc-400 mb-4 uppercase tracking-wider">Terminal Output</h3>
                {error && (
                  <div className="mb-4 bg-red-950/50 border border-red-900/50 rounded-lg p-3 flex items-start space-x-3 text-red-200 text-sm">
                    <AlertCircle size={16} className="text-red-400 mt-0.5 shrink-0" />
                    <span>{error}</span>
                  </div>
                )}
                <div className="bg-zinc-950 rounded-lg p-4 font-mono text-xs text-zinc-400 h-64 overflow-y-auto whitespace-pre-wrap">
                  {logs}
                </div>
              </div>
            )}
          </div>

          {/* Preview Column */}
          <div className="lg:col-span-8">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 min-h-[600px] shadow-2xl flex flex-col">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-semibold tracking-tight text-white">Live Preview</h2>
                {slides.length > 0 && (
                  <button 
                    onClick={() => {
                        const link = document.createElement('a');
                        link.href = '/api/download';
                        link.download = 'carousel_export.zip';
                        link.click();
                    }}
                    className="text-sm font-medium bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-md transition-colors flex items-center space-x-2 border border-zinc-700"
                  >
                    <Download size={16} />
                    <span>Download All Zip</span>
                  </button>
                )}
              </div>
              
              {loading ? (
                <div className="flex-1 flex flex-col items-center justify-center text-zinc-500 fade-in">
                  <div className="relative">
                    <div className="w-16 h-16 border-4 border-zinc-800 border-t-blue-500 rounded-full animate-spin"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 size={24} className="text-blue-500 animate-pulse" />
                    </div>
                  </div>
                  <p className="mt-6 text-sm tracking-wide font-medium">Executing deterministic rendering engine...</p>
                </div>
              ) : slides.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                  {slides.map((src, i) => (
                    <div key={i} className="group relative aspect-[4/5] bg-zinc-950 rounded-xl overflow-hidden border border-zinc-800 shadow-xl flex flex-col">
                      {editingIndex === i ? (
                        <div className="absolute inset-0 p-4 bg-zinc-900 flex flex-col z-10 w-full h-full space-y-3 overflow-y-auto">
                          <div className="flex justify-between items-center mb-1 shrink-0">
                             <h4 className="text-sm font-medium">Edit Slide {i + 1}</h4>
                             <button onClick={() => setEditingIndex(null)} className="text-zinc-400 hover:text-white p-1">
                                <X size={16} />
                             </button>
                          </div>
                          <div className="shrink-0">
                              <label className="block text-xs text-zinc-500 mb-1">Title</label>
                              <textarea 
                                value={editTitle}
                                onChange={e => setEditTitle(e.target.value)}
                                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-zinc-100 resize-none h-16 shrink-0 focus:outline-none focus:border-blue-500"
                              />
                          </div>
                          <div className="shrink-0">
                              <label className="block text-xs text-zinc-500 mb-1">Body</label>
                              <textarea 
                                value={editBody}
                                onChange={e => setEditBody(e.target.value)}
                                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-zinc-100 resize-none h-24 shrink-0 focus:outline-none focus:border-blue-500"
                              />
                          </div>
                          <button 
                            onClick={saveSlideEdit}
                            className="w-full shrink-0 mt-auto bg-blue-600 hover:bg-blue-500 text-white text-sm py-2 rounded-md flex items-center justify-center space-x-2"
                          >
                            <Check size={14} /> <span>Save & Render</span>
                          </button>
                        </div>
                      ) : (
                        <>
                            <img 
                                src={src} 
                                alt={`Slide ${i + 1}`} 
                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                            />
                            
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/0 to-black/0 opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-between p-4 pointer-events-none">
                                <span className="text-white text-sm font-medium">Slide {i + 1}</span>
                            </div>
                            
                            {contentPlan.length > 0 && (
                                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center space-y-3">
                                    <button 
                                        onClick={() => startEdit(i)}
                                        className="w-32 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-md px-4 py-2 text-sm font-medium text-white flex items-center justify-center space-x-2 border border-white/20 shadow-lg transition-transform hover:scale-105"
                                    >
                                        <Edit2 size={14} /> <span>Edit Text</span>
                                    </button>
                                    <button 
                                        onClick={() => window.open(src, '_blank')}
                                        className="w-32 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-md px-4 py-2 text-sm font-medium text-white flex items-center justify-center space-x-2 border border-white/20 shadow-lg transition-transform hover:scale-105"
                                    >
                                        <ImageIcon size={14} /> <span>Preview</span>
                                    </button>
                                    <button 
                                        onClick={() => {
                                            const link = document.createElement('a');
                                            link.href = src;
                                            link.download = `slide_${i + 1}.jpg`;
                                            link.click();
                                        }}
                                        className="w-32 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-md px-4 py-2 text-sm font-medium text-white flex items-center justify-center space-x-2 border border-white/20 shadow-lg transition-transform hover:scale-105"
                                    >
                                        <Download size={14} /> <span>Save</span>
                                    </button>
                                </div>
                            )}

                            <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-md rounded-md px-2 py-1 text-xs font-medium text-white border border-white/10 pointer-events-none">
                                {String(i + 1).padStart(2, '0')}
                            </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center text-zinc-600 border-2 border-dashed border-zinc-800 rounded-xl">
                  <div className="text-center">
                    <ImageIcon size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No slides generated yet.</p>
                    <p className="text-sm mt-1">Configure your campaign on the left to begin.</p>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
