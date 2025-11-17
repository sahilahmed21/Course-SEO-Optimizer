import React from 'react';

export function WorkflowProgress({ isLoading, isComplete }) {
    let node = 0;
    let progress = 0;
    if (isLoading) {
        node = 1; // Simulating "Analyzing Competitors"
        progress = 47;
    }
    if (isComplete) {
        node = 4;
        progress = 100;
    }

    return (
        <footer className="workflow-footer">
            <button className="btn btn-primary" disabled={isLoading}>
                {isLoading ? 'Running...' : 'Run All Nodes Sequentially'}
            </button>
            <div style={{ flex: 1, padding: '0 2rem' }}>
                <div className="score-card-bar">
                    <div
                        className="bar-inner bar-blue"
                        style={{
                            width: `${progress}%`,
                            transition: 'width 0.5s ease'
                        }}
                    ></div>
                </div>
            </div>
            <span style={{ color: 'var(--text-light)', fontSize: '0.9rem' }}>Node {node} of 4</span>
        </footer>
    );
}