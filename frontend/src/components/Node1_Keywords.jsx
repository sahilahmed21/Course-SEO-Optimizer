import React from 'react';

export function Node1_Keywords({ data }) {
    return (
        <div>
            <div className="stats-grid">
                <div className="stat-card">
                    <h3 className="stat-card-title">Performance Score</h3>
                    <div className="stat-card-value">{data.performance_score}%</div>
                </div>
                {/* We omit "Courses Scanned" and "Keywords Found" as they are mock data */}
            </div>

            <div className="keyword-category">
                <h3>Must-Have Keywords</h3>
                {data.must_have_keywords.map((kw, i) => (
                    <span key={i} className="keyword-chip chip-blue">{kw}</span>
                ))}
            </div>
            <div className="keyword-category">
                <h3>Trending Keywords</h3>
                {data.trending_keywords.map((kw, i) => (
                    <span key={i} className="keyword-chip chip-gray">{kw}</span>
                ))}
            </div>
        </div>
    );
}