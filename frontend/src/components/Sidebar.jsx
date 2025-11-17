import React, { useState } from 'react';

// --- Our 3 Target Courses ---
// We define our course data here
const courses = [
    {
        name: "Select a course to audit...",
        url: "",
        query: ""
    },
    {
        name: "BA (Hons) Accounting & Finance",
        url: "https://www.uwl.ac.uk/course/undergraduate/accounting-and-finance?start=1650&option=33",
        query: "BA (Hons) Accounting & Finance UK" // Using a better search query
    },
    {
        name: "BSc (Hons) Cyber Security",
        url: "https://www.uwl.ac.uk/course/undergraduate/cyber-security?start=1650&option=33",
        query: "BSc (Hons) Cyber Security UK"
    },
    {
        name: "BA (Hons) Fashion: Design and Accessories",
        url: "https://www.uwl.ac.uk/course/undergraduate/fashion-design-and-accessories?start=1730&option=33",
        query: "BA (Hons) Fashion Design UK" // Using a better search query
    }
];

export function Sidebar({ onAnalyze, isLoading }) {
    // The state is now just the index of the selected course
    const [selectedIndex, setSelectedIndex] = useState(0);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (selectedIndex === 0) {
            alert('Please select a course to analyze.');
            return;
        }

        // Get the data from our selected course
        const selectedCourse = courses[selectedIndex];

        onAnalyze({
            targetUrl: selectedCourse.url,
            query: selectedCourse.query
        });
    };

    const handleReset = () => {
        setSelectedIndex(0);
        // We might also want to tell the App to clear the report
        // but for now, this just resets the dropdown.
    }

    return (
        <aside className="app-sidebar">
            <h2 className="sidebar-title">Filters</h2>

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="course-select">Select Target Course</label>

                    {/* --- This is the new Dropdown --- */}
                    <select
                        id="course-select"
                        className="form-input" // We can reuse the input style
                        value={selectedIndex}
                        onChange={(e) => setSelectedIndex(e.target.value)}
                        disabled={isLoading}
                    >
                        {courses.map((course, index) => (
                            <option key={index} value={index} disabled={index === 0}>
                                {course.name}
                            </option>
                        ))}
                    </select>

                </div>

                {/* The text inputs are now gone */}

                <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={isLoading}>
                    {isLoading ? 'Analyzing...' : 'Apply Filters'}
                </button>
                <button
                    type="button"
                    onClick={handleReset}
                    style={{ width: '100%', marginTop: '0.5rem', background: 'none', border: 'none', color: 'var(--text-light)', cursor: 'pointer' }}
                    disabled={isLoading}
                >
                    Reset
                </button>
            </form>
        </aside>
    );
}