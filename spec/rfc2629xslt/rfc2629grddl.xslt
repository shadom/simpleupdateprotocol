<!--
    GRDDL transformation for RFC2629 XML format

    Copyright (c) 2007, Julian Reschke (julian.reschke@greenbytes.de)
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of Julian Reschke nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
-->

<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               version="1.0"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:dc="http://purl.org/dc/elements/1.1/"
               >

<xsl:import href="rfc2629.xslt"/>
               
<xsl:output indent="yes" method="xml" version="1.0"/>
               
<xsl:template match="/">
  <rdf:RDF>

    <rdf:Description rdf:about="">
      <!-- title -->
      <dc:title><xsl:value-of select="/rfc/front/title"/></dc:title>
  
      <!-- authors -->
      <xsl:for-each select="/rfc/front/author">
        <xsl:variable name="initials">
          <xsl:call-template name="format-initials"/>
        </xsl:variable>
        <dc:creator><xsl:value-of select="concat(@surname,', ',$initials)"/></dc:creator>
      </xsl:for-each>
      
      <!-- issued -->
      <xsl:variable name="month"><xsl:call-template name="get-month-as-num"/></xsl:variable>
      <dc:issued><xsl:value-of select="concat(/rfc/front/date/@year,'-',$month)"/></dc:issued>
  
    </rdf:Description>

  </rdf:RDF>
</xsl:template>
 
</xsl:transform>