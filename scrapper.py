const express = require('express');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const open = require('open');

const app = express();
const PORT = 3028;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Endpoint to get alumni data
app.get('/get-alumni-data', (req, res) => {
    try {
        const fileName = `alumni_data_after_2023_${new Date().toISOString().split('T')[0]}.txt`;
        if (!fs.existsSync(fileName)) {
            return res.status(404).json({ error: 'No data file found' });
        }

        const content = fs.readFileSync(fileName, 'utf8');
        const alumniData = parseAlumniData(content);
        res.json(alumniData);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

function parseAlumniData(content) {
    const alumni = [];
    const sections = content.split('=== Scraping Session:').slice(1);
    
    sections.forEach(section => {
        const lines = section.split('\n');
        let currentAlumni = {};
        
        lines.forEach(line => {
            if (line.startsWith('Name:')) {
                if (Object.keys(currentAlumni).length > 0) {
                    alumni.push(currentAlumni);
                }
                currentAlumni = {
                    name: line.replace('Name:', '').trim()
                };
            } else if (line.startsWith('Location:')) {
                currentAlumni.location = line.replace('Location:', '').trim();
            } else if (line.startsWith('Class:')) {
                currentAlumni.class = line.replace('Class:', '').trim();
            } else if (line.startsWith('Course:')) {
                currentAlumni.course = line.replace('Course:', '').trim();
            }
        });
        
        if (Object.keys(currentAlumni).length > 0) {
            alumni.push(currentAlumni);
        }
    });
    
    return alumni;
}

async function Scrapper() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    const AlumniData = [];
    
    // Create or clear the output file at the start
    const fileName = `alumni_data_after_2023_${new Date().toISOString().split('T')[0]}.txt`;
    
    // Add timestamp and separator for new scraping session
    const timestamp = new Date().toLocaleString();
    const separator = `\n\n=== Scraping Session: ${timestamp} ===\n\n`;
    
    // Check if file exists, if not create it
    if (!fs.existsSync(fileName)) {
        fs.writeFileSync(fileName, '', 'utf8');
    }
    
    // Append separator for new session
    fs.appendFileSync(fileName, separator, 'utf8');
    
    await page.goto('https://alumni.uohyd.ac.in/members').then(() => {
        console.log(`Website Reached`);
    });

    await page.waitForSelector("#email");
    await page.type(`#email`, `23mcce13@uohyd.ac.in`, { delay: 100 });
    await new Promise(r => setTimeout(r, 1000));
    await page.click(`#emailBtn`);
    await new Promise(r => setTimeout(r, 3000));
    await page.waitForSelector(`#passwordLogin`);
    await page.type(`#passwordLogin`, `Shankar@8168`);
    await page.waitForSelector(`#inside-ui-view > ui-view > main > div.mdl-grid.login-size.contact-div-change.main-family > div > div > div.mdl-cell.mdl-cell--12-col-tablet.login-top-div.login-signup-padding.flexbox.mdl-cell--7-col.login-border > div > form > div:nth-child(4) > button.mdl-button.font-14.ladda-button.ladda-button-primary.mdl-js-button.mdl-button--raised.mdl-button--colored.mdl-typography--font-regular`);
    await page.click(`#inside-ui-view > ui-view > main > div.mdl-grid.login-size.contact-div-change.main-family > div > div > div.mdl-cell.mdl-cell--12-col-tablet.login-top-div.login-signup-padding.flexbox.mdl-cell--7-col.login-border > div > form > div:nth-child(4) > button.mdl-button.font-14.ladda-button.ladda-button-primary.mdl-js-button.mdl-button--raised.mdl-button--colored.mdl-typography--font-regular`);
    await page.waitForNavigation().then(() => {
        console.log('Successfully logged in');
    });

    const selector = '[ng-click*="select_in_level"]';
    await page.waitForSelector(selector);
    const totalCards = (await page.$$(selector)).length;

    // Start from the 6th card (2023 batch)
    for (let j = 5; j < totalCards; j++) {
        await page.waitForSelector(selector);
        const cards = await page.$$(selector);
        const card = cards[j];

        const title = await card.$eval('span', el => el.textContent.trim());
        console.log(`Processing batch: ${title}`);

        await card.click().then(async () => {
            const selector1 = '[ng-click*="count_obj2.key"]';
            await page.waitForSelector(selector1);
            const totalChildCards = (await page.$$(selector1)).length;
            await page.waitForSelector(".mdl-cell.mdl-cell--12-col.left-alignment.font-18");
            
            for (let i = 0; i < totalChildCards; i++) {
                await page.waitForSelector(selector1);
                const ChildCards = await page.$$(selector1);
                const Ccard = ChildCards[i];
                const titleChild = await Ccard.$eval('span', el => el.textContent.trim());
                console.log(`Processing: ${titleChild}`);
                
                await Ccard.click().then(async () => {
                    await page.waitForSelector('.maximize-width.border-box.padding-12');
                    const memberCards = await page.$$('.maximize-width.border-box.padding-12');
                    await page.waitForSelector('.font-16.font-xs-14.mdl-typography--font-medium');
                    var course = await page.$eval('.font-16.font-xs-14.mdl-typography--font-medium', el => el.textContent.trim());
                    const splitted = course.split(",");
                    course = splitted[1];
                    
                    for (const card of memberCards) {
                        const name = await card.$eval('a.link-detail', el => el.textContent.trim());
                        try {
                            var location = await card.$eval('div.overflow-ellipsis', el => el.textContent.trim());
                        } catch (err) {
                            var location = "Unknown";
                        }
                        
                        const record = {
                            name: name,
                            location: location,
                            class: title,
                            course: course
                        };

                        // Write each record to file in text format
                        const textLine = `Name: ${name}\nLocation: ${location}\nClass: ${title}\nCourse: ${course}\n${'-'.repeat(50)}\n`;
                        fs.appendFileSync(fileName, textLine, 'utf8');

                        AlumniData.push(record);
                        console.log(`Saved: ${name}, ${location}, ${title}, ${course}`);
                    }
                });
                await page.goBack();
            }
        });
        await page.goBack();
    }

    console.log(`File saved successfully: ${fileName}`);
    console.log(`Total records saved: ${AlumniData.length}`);

    await browser.close();
}

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    // Open the browser automatically
    open(`http://localhost:${PORT}`).catch(err => {
        console.error('Could not open browser:', err);
    });
    Scrapper();
});
