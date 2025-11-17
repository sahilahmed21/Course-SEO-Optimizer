import React, { useState } from 'react';
import axios from 'axios';
import './index.css';

// --- Import Components ---
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { WorkflowProgress } from './components/WorkflowProgress';
import { WorkflowNode } from './components/WorkflowNode';
import { Node1_Keywords } from './components/Node1_Keywords';
import { Node2_Competitors } from './components/Node2_Competitors';
import { Node3_Content } from './components/Node3_Content';
import { Node5_Metadata } from './components/Node5_Metadata';
// Node 6 is removed
import { FinalScores } from './components/FinalScores'; // Renamed

// The URL of our FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function App() {
    const [jobId, setJobId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [reportData, setReportData] = useState(null);
    const [error, setError] = useState(null);

    let pollInterval;

    // --- API Polling Logic ---
    const pollForResults = (id) => {
        pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/results/${id}`);
                const { status, report, error: jobError } = response.data;

                if (status === 'COMPLETE') {
                    clearInterval(pollInterval);
                    setIsLoading(false);
                    setReportData(report);
                    setError(null);
                } else if (status === 'FAILED') {
                    clearInterval(pollInterval);
                    setIsLoading(false);
                    setError(jobError || 'The analysis failed to complete.');
                    setReportData(null);
                }
            } catch (err) {
                clearInterval(pollInterval);
                setIsLoading(false);
                setError('Failed to fetch results from the server.');
            }
        }, 5000);
    };

    // --- API Start Logic ---
    const handleAnalyze = async ({ targetUrl, query }) => {
        setIsLoading(true);
        setReportData(null);
        setError(null);
        setJobId(null);
        if (pollInterval) clearInterval(pollInterval);

        try {
            const response = await axios.post(`${API_BASE_URL}/analyze`, {
                target_url: targetUrl,
                query: query,
            });

            const { job_id } = response.data;
            if (job_id) {
                setJobId(job_id);
                pollForResults(job_id);
            } else {
                throw new Error('No Job ID received from server.');
            }
        } catch (err) {
            setIsLoading(false);
            setError(err.response?.data?.detail || err.message || 'Failed to start analysis.');
        }
    };

    // --- Render Functions ---

    const renderContent = () => {
        if (isLoading) {
            return (
                <WorkflowNode icon="" title="Loading all nodes...">
                    <Node2_Competitors data={null} isLoading={true} />
                </WorkflowNode>
            );
        }

        if (error) {
            return <div className="error-message"><strong>Error:</strong> {error}</div>;
        }

        if (reportData) {
            // We have data, render all the nodes
            return (
                <>
                    {/* --- The 4 Nodes --- */}
                    <WorkflowNode icon="" title="Node 1: Keyword & Performance Scan">
                        <Node1_Keywords data={reportData.node_1_keywords} />
                    </WorkflowNode>

                    <WorkflowNode icon="" title="Node 2: Competitive Benchmarking">
                        <Node2_Competitors data={reportData.node_2_competitors} />
                    </WorkflowNode>

                    <WorkflowNode icon="" title="Node 3: Content Rewrite & Enhancement">
                        <Node3_Content data={reportData.node_3_content_rewrite} />
                    </WorkflowNode>

                    <WorkflowNode icon="" title="Node 4: Metadata Generation">
                        <Node5_Metadata data={reportData.node_5_metadata} />
                    </WorkflowNode>

                    {/* --- Static Apply Button --- */}
                    <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '1rem 0' }}>
                        <button className="btn btn-primary" onClick={() => alert('Changes applied! (Demo)')}>
                            Apply Changes
                        </button>
                    </div>

                    <hr style={{ border: 0, borderTop: '1px solid var(--border-color)', margin: '2rem 0' }} />

                    {/* --- Final Scores Block (Not a Node) --- */}
                    <FinalScores data={reportData.final_scores} />
                </>
            );
        }

        // Default empty state
        return <div style={{ color: "var(--text-light)" }}>Click "Apply Filters" in the sidebar to run an audit.</div>;
    };

    return (
        <>
            <Header />
            <div className="app-wrapper">
                <Sidebar onAnalyze={handleAnalyze} isLoading={isLoading} />
                <main className="main-content">
                    {renderContent()}
                </main>
            </div>
            <WorkflowProgress
                isLoading={isLoading}
                isComplete={!!reportData}
            />
        </>
    );
}

export default App;