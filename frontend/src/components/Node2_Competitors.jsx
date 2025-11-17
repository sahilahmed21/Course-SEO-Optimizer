import React from 'react';

export function Node2_Competitors({ data, isLoading = false }) {
    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p style={{ color: 'var(--text-light)' }}>Processing... 47%</p>
                <p style={{ fontWeight: 600 }}>Analyzing competitors...</p>
            </div>
        );
    }

    return (
        <table className="qa-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Competitor Page</th>
                    <th>Top Keywords</th>
                    <th>Differentiator</th>
                </tr>
            </thead>
            <tbody>
                {data.top_competitors.map((c) => (
                    <tr key={c.rank}>
                        <td style={{ fontWeight: 600 }}>#{c.rank}</td>
                        <td>
                            <a href={c.url} target="_blank" rel="noopener noreferrer">
                                {c.name}
                            </a>
                        </td>
                        <td>{c.top_keywords.join(', ')}</td>
                        <td>{c.differentiator}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}