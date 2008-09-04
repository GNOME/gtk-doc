<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

  <!-- import the chunked fo stylesheet -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>

  <!-- change some parameters -->
  <xsl:attribute-set name="monospace.verbatim.properties">
    <!--xsl:attribute name="font-family">Monospace</xsl:attribute-->
    <xsl:attribute name="font-size">7pt</xsl:attribute>
    <xsl:attribute name="keep-together.within-column">always</xsl:attribute>
  </xsl:attribute-set>
  
  <xsl:param name="shade.verbatim" select="1"/>

  <xsl:attribute-set name="shade.verbatim.style">
    <xsl:attribute name="background-color">#D0D0D0</xsl:attribute>
    <xsl:attribute name="border-width">0.5pt</xsl:attribute>
    <xsl:attribute name="border-style">solid</xsl:attribute>
    <xsl:attribute name="border-color">#575757</xsl:attribute>
    <xsl:attribute name="padding">3pt</xsl:attribute>
  </xsl:attribute-set>

  <xsl:attribute-set name="xref.properties">
    <xsl:attribute name="color">
      <xsl:choose>
        <xsl:when test="self::ulink">blue</xsl:when>
        <xsl:otherwise>inherit</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:attribute-set>

</xsl:stylesheet>

