import React from 'react';

export function Header() {
    // We can add search functionality later
    return (
        <header className="app-header">
            <span className="header-title">UWL Course & Program Optimization Console</span>
            <button className="btn btn-primary">Start New SEO Audit</button>
        </header>
    );
}