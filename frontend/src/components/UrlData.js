import React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Typography from '@mui/material/Typography';

const UrlData = ({ url, links }) => (
  <Accordion>
    <AccordionSummary
      expandIcon={<ExpandMoreIcon />}
      aria-controls="panel1a-content"
      id="panel1a-header"
    >
      <Typography>{url}</Typography>
    </AccordionSummary>
    <AccordionDetails>
      <Typography component={'div'}>
        <ul>
          {links.map((link, index) => (
            <li key={index}><a href={link} target="_blank" rel="noopener noreferrer">{link}</a></li>
          ))}
        </ul>
      </Typography>
    </AccordionDetails>
  </Accordion>
);

export default UrlData;
